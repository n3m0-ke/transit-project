import os
from django.conf import settings
import json
import logging
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from rtree import index as rtree_index
from dotenv import load_dotenv
import redis


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = settings.BASE_DIR  # Gets the absolute base directory
GTFS_DIR = os.path.join(BASE_DIR, "data", "gtfs")  # Constructs a system-friendly GTFS path

FILES = ["stops", "routes", "trips", "stop_times"]


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# --- Redis Setup & Utilities ---

load_dotenv()

def get_redis_client():
    """Attempts to connect to Redis Cloud."""
    try:
        client = redis.StrictRedis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            username=os.getenv("REDIS_USERNAME"),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB")),
            decode_responses=True
        )
        client.ping()  # Test connection
        return client
    except redis.ConnectionError:
        return None  # Handle offline mode gracefully


redis_client = get_redis_client()

def cache_to_redis(key, data):
    if redis_client:
        try:
            redis_client.set(key, json.dumps(data))
            logger.info(f"Cached {key} to Redis.")
        except Exception as e:
            logger.error(f"Failed to cache {key}: {e}")

def load_from_redis(key):
    if redis_client:
        try:
            cached = redis_client.get(key)
            if cached:
                logger.info(f"Loaded {key} from Redis.")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Error reading {key} from Redis: {e}")
    return None

# --- GTFS Data ---

def load_gtfs_data():
    """Loads GTFS data from Redis cache or from CSV files, ensuring files exist."""
    cached_data = load_from_redis("gtfs_data")
    if cached_data:
        return cached_data

    logger.info("Loading GTFS data from CSV files...")
    gtfs_data = {}

    for file in FILES:
        path = os.path.join(GTFS_DIR, f"{file}.txt")  # ✅ OS-friendly path handling

        # Explicitly check if file exists before loading
        if not os.path.exists(path):
            logger.error(f"GTFS file not found: {path}")
            raise FileNotFoundError(f"Missing GTFS file: {path}")

        df = pd.read_csv(path)
        gtfs_data[file] = df.to_dict(orient="records")

    cache_to_redis("gtfs_data", gtfs_data)
    return gtfs_data

# --- Geo & Spatial Indexing ---

def get_stops_gdf(gtfs_data):
    """Returns a GeoDataFrame of stops with geometry."""
    stops_df = pd.DataFrame(gtfs_data["stops"])
    stops_df["geometry"] = stops_df.apply(lambda row: Point(float(row["stop_lon"]), float(row["stop_lat"])), axis=1)
    return gpd.GeoDataFrame(stops_df, geometry="geometry", crs="EPSG:4326")

def build_spatial_index(stops_gdf):
    """Builds an R-tree spatial index."""
    idx = rtree_index.Index()
    for i, row in stops_gdf.iterrows():
        idx.insert(i, row.geometry.bounds)
    return idx

# --- Nearest Stops ---

def find_nearest_stops(user_location, stops_gdf, spatial_idx, radius_km=1.0):
    """Finds stops within a given radius of user_location (lat, lon)."""
    lat, lon = user_location
    cache_key = f"nearest_stops:{lat:.5f}_{lon:.5f}_{radius_km:.1f}"
    
    cached_result = load_from_redis(cache_key)
    if cached_result:
        return cached_result

    user_point = Point(lon, lat)
    buffer_radius_deg = radius_km / 111  # Approximate deg/km
    bounds = user_point.buffer(buffer_radius_deg).bounds
    matches = list(spatial_idx.intersection(bounds))

    nearby_stops = stops_gdf.iloc[matches].copy()
    nearby_stops = nearby_stops[nearby_stops["geometry"].within(user_point.buffer(buffer_radius_deg))]

    result = nearby_stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]].to_dict(orient="records")
    cache_to_redis(cache_key, result)
    return result

# --- Trip + Route Utilities ---

def get_route_trips(gtfs_data, route_id):
    """Fetches trips associated with a given route."""
    return [trip for trip in gtfs_data["trips"] if trip["route_id"] == route_id]

def get_trip_stop_times(gtfs_data, trip_id):
    """Fetches stop times for a given trip."""
    stop_times = [st for st in gtfs_data["stop_times"] if st["trip_id"] == trip_id]
    return sorted(stop_times, key=lambda x: int(x["stop_sequence"]))

def search_routes_by_name(gtfs_data, route_name):
    """Finds routes matching the given name or ID."""
    routes = pd.DataFrame(gtfs_data["routes"])
    matched_routes = routes[routes["route_long_name"].str.contains(route_name, case=False, na=False)]
    return matched_routes[["route_id", "route_long_name", "route_type"]].to_dict(orient="records")

from datetime import datetime, timedelta

def get_next_trips(gtfs_data, stop_id, time_window=30):
    """Find upcoming trips from a given stop ID within a time window (minutes)."""
    now = datetime.now().strftime("%H:%M:%S")

    relevant_stop_times = [
        st for st in gtfs_data["stop_times"]
        if st["stop_id"] == stop_id and st.get("departure_time")
    ]
    upcoming = []
    for st in relevant_stop_times:
        dep_time = st["departure_time"]
        if dep_time > now:
            upcoming.append(st)
    upcoming = sorted(upcoming, key=lambda x: x["departure_time"])
    return upcoming[:5]

def calculate_path(gtfs_data, start_stop_id, end_stop_id):
    """A mock placeholder to compute a simple path (can be upgraded with graphs later)."""
    # For now, return a direct connection if both stops are in the same trip
    trips_with_start = {
        st["trip_id"] for st in gtfs_data["stop_times"] if st["stop_id"] == start_stop_id
    }
    trips_with_end = {
        st["trip_id"] for st in gtfs_data["stop_times"] if st["stop_id"] == end_stop_id
    }
    common_trips = trips_with_start.intersection(trips_with_end)

    if common_trips:
        trip_id = list(common_trips)[0]
        stop_times = get_trip_stop_times(gtfs_data, trip_id)
        path = [st for st in stop_times if st["stop_id"] in [start_stop_id, end_stop_id]]
        return path
    return []

def get_stop_coordinates(gtfs_data, stop_id):
    """Returns coordinates of a given stop_id."""
    for stop in gtfs_data["stops"]:
        if stop["stop_id"] == stop_id:
            return {
                "lat": float(stop["stop_lat"]),
                "lon": float(stop["stop_lon"]),
                "stop_name": stop.get("stop_name")
            }
    return {}

def get_routes_by_stop(gtfs_data, stop_id):
    """Returns routes serving a stop by checking stop_times -> trips -> routes."""
    trip_ids = {st["trip_id"] for st in gtfs_data["stop_times"] if st["stop_id"] == stop_id}
    route_ids = {
        trip["route_id"] for trip in gtfs_data["trips"] if trip["trip_id"] in trip_ids
    }
    return [
        route for route in gtfs_data["routes"] if route["route_id"] in route_ids
    ]

def get_trip_stops(gtfs_data, trip_id):
    """Returns all stops along a trip."""
    stop_times = get_trip_stop_times(gtfs_data, trip_id)
    stops = []
    for st in stop_times:
        stop = next((s for s in gtfs_data["stops"] if s["stop_id"] == st["stop_id"]), None)
        if stop:
            stops.append({
                "stop_id": stop["stop_id"],
                "stop_name": stop.get("stop_name"),
                "lat": float(stop["stop_lat"]),
                "lon": float(stop["stop_lon"]),
                "arrival_time": st.get("arrival_time"),
                "departure_time": st.get("departure_time"),
                "sequence": st.get("stop_sequence"),
            })
    return stops

def get_departure_board(gtfs_data, stop_id, time_window=30):
    """Returns upcoming departures at a stop within the given time window."""
    now = datetime.now()
    end_time = (now + timedelta(minutes=time_window)).strftime("%H:%M:%S")

    departures = [
        st for st in gtfs_data["stop_times"]
        if st["stop_id"] == stop_id and now.strftime("%H:%M:%S") <= st["departure_time"] <= end_time
    ]
    return sorted(departures, key=lambda x: x["departure_time"])[:10]


# --- Initialization ---

# Load and initialize once if needed
gtfs_data = load_gtfs_data()
stops_gdf = get_stops_gdf(gtfs_data)
spatial_idx = build_spatial_index(stops_gdf)

# --- Example usage ---

if __name__ == "__main__":
    user_location = (-1.286389, 36.817223)  # Nairobi CBD
    nearby = find_nearest_stops(user_location, stops_gdf, spatial_idx)
    print("Nearby stops:")
    for stop in nearby:
        print(f"{stop['stop_id']} - {stop['stop_name']}")
