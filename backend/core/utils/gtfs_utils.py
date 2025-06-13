import os
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from rtree import index as rtree_index
from dotenv import load_dotenv
import redis
from django.conf import settings

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

BASE_DIR = settings.BASE_DIR
GTFS_DIR = os.path.join(BASE_DIR, "data", "gtfs")
FILES = ["stops", "routes", "trips", "stop_times"]

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# --- Redis Setup ---
def get_redis_client():
    try:
        client = redis.StrictRedis(
            host=os.getenv("REDIS_HOST"),
            port=REDIS_PORT,
            username=os.getenv("REDIS_USERNAME"),
            password=os.getenv("REDIS_PASSWORD"),
            db=REDIS_DB,
            decode_responses=True
        )
        client.ping()
        return client
    except redis.ConnectionError:
        logger.warning("Redis unavailable, caching disabled.")
        return None

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
            logger.error(f"Redis read error for {key}: {e}")
    return None

# --- GTFS Data Load ---
def load_gtfs_data():
    """Load GTFS data from cache or local CSV files."""
    cached_data = load_from_redis("gtfs_data")
    if cached_data:
        return cached_data

    logger.info("Loading GTFS data from CSV files...")
    gtfs_data = {}

    for file in FILES:
        path = os.path.join(GTFS_DIR, f"{file}.txt")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing GTFS file: {path}")
        df = pd.read_csv(path)
        gtfs_data[file] = df.to_dict(orient="records")

    cache_to_redis("gtfs_data", gtfs_data)
    return gtfs_data

# --- Geo and Spatial Index ---
def get_stops_gdf(gtfs_data):
    """Convert stops into a GeoDataFrame."""
    stops_df = pd.DataFrame(gtfs_data["stops"])
    stops_df["geometry"] = stops_df.apply(
        lambda row: Point(float(row["stop_lon"]), float(row["stop_lat"])), axis=1
    )
    return gpd.GeoDataFrame(stops_df, geometry="geometry", crs="EPSG:4326")

def build_spatial_index(stops_gdf):
    """Build an R-tree index for spatial search."""
    idx = rtree_index.Index()
    for i, row in stops_gdf.iterrows():
        idx.insert(i, row.geometry.bounds)
    return idx

def find_nearest_stops(user_location, stops_gdf, spatial_idx, radius_km=1.0):
    """Find nearby stops within a radius (km) of a lat/lon point."""
    lat, lon = user_location
    cache_key = f"nearest_stops:{lat:.5f}_{lon:.5f}_{radius_km:.1f}"

    cached_result = load_from_redis(cache_key)
    if cached_result:
        return cached_result

    user_point = Point(lon, lat)
    buffer_radius_deg = radius_km / 111  # Rough conversion
    bounds = user_point.buffer(buffer_radius_deg).bounds
    matches = list(spatial_idx.intersection(bounds))

    nearby_stops = stops_gdf.iloc[matches].copy()
    nearby_stops = nearby_stops[nearby_stops["geometry"].within(user_point.buffer(buffer_radius_deg))]

    result = nearby_stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]].to_dict(orient="records")
    cache_to_redis(cache_key, result)
    return result

# --- Trip & Route Utilities ---
def get_route_trips(gtfs_data, route_id):
    return [trip for trip in gtfs_data["trips"] if trip["route_id"] == route_id]

def get_trip_stop_times(gtfs_data, trip_id):
    stop_times = [st for st in gtfs_data["stop_times"] if st["trip_id"] == trip_id]
    return sorted(stop_times, key=lambda x: int(x["stop_sequence"]))

def search_routes_by_name(gtfs_data, route_name):
    routes = pd.DataFrame(gtfs_data["routes"])
    matched = routes[routes["route_long_name"].str.contains(route_name, case=False, na=False)]
    return matched[["route_id", "route_long_name", "route_type"]].to_dict(orient="records")

def get_next_trips(gtfs_data, stop_id, time_window=30):
    """Get the next 5 trips departing from a stop."""
    now = datetime.now().strftime("%H:%M:%S")
    candidates = [
        st for st in gtfs_data["stop_times"]
        if st["stop_id"] == stop_id and st.get("departure_time") > now
    ]
    upcoming = sorted(candidates, key=lambda x: x["departure_time"])
    return upcoming[:5]

def get_trip_stops(gtfs_data, trip_id):
    """Get ordered list of stops for a given trip."""
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

def get_routes_by_stop(gtfs_data, stop_id):
    """Return all routes passing through a given stop."""
    trip_ids = {st["trip_id"] for st in gtfs_data["stop_times"] if st["stop_id"] == stop_id}
    route_ids = {
        trip["route_id"] for trip in gtfs_data["trips"] if trip["trip_id"] in trip_ids
    }
    return [route for route in gtfs_data["routes"] if route["route_id"] in route_ids]

def get_stop_coordinates(gtfs_data, stop_id):
    for stop in gtfs_data["stops"]:
        if stop["stop_id"] == stop_id:
            return {
                "lat": float(stop["stop_lat"]),
                "lon": float(stop["stop_lon"]),
                "stop_name": stop.get("stop_name"),
            }
    return {}

def get_departure_board(gtfs_data, stop_id, time_window=30):
    """Upcoming departures at a stop."""
    now = datetime.now()
    end_time = (now + timedelta(minutes=time_window)).strftime("%H:%M:%S")

    departures = [
        st for st in gtfs_data["stop_times"]
        if st["stop_id"] == stop_id and now.strftime("%H:%M:%S") <= st["departure_time"] <= end_time
    ]
    return sorted(departures, key=lambda x: x["departure_time"])[:10]

def calculate_path(gtfs_data, start_stop_id, end_stop_id):
    """Returns direct path between stops if they share a trip."""
    trips_with_start = {
        st["trip_id"] for st in gtfs_data["stop_times"] if st["stop_id"] == start_stop_id
    }
    trips_with_end = {
        st["trip_id"] for st in gtfs_data["stop_times"] if st["stop_id"] == end_stop_id
    }
    common_trips = trips_with_start & trips_with_end
    if common_trips:
        trip_id = list(common_trips)[0]
        return get_trip_stops(gtfs_data, trip_id)
    return []
