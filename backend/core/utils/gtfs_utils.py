import pandas as pd
import redis
import json
import geopandas as gpd
from shapely.geometry import Point
from rtree import index  # Spatial indexing

# Connect to Redis (Use ENV variables for production)
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

GTFS_DIR = "core/data/gtfs"
FILES = ["stops", "trips", "routes", "stop_times"]

# Cache GTFS data in Redis
def load_gtfs_data():
    """Loads GTFS CSVs and caches them in Redis."""
    if redis_client.exists("gtfs_data"):
        return json.loads(redis_client.get("gtfs_data"))
    
    gtfs_data = {file: pd.read_csv(f"{GTFS_DIR}/{file}.txt").to_dict() for file in FILES}
    redis_client.set("gtfs_data", json.dumps(gtfs_data))
    return gtfs_data

# Spatial Indexing
def get_stops_gdf(gtfs_data):
    stops_df = pd.DataFrame(gtfs_data["stops"])
    stops_df["geometry"] = stops_df.apply(lambda row: Point(row["stop_lon"], row["stop_lat"]), axis=1)
    return gpd.GeoDataFrame(stops_df, geometry="geometry", crs="EPSG:4326")

def build_spatial_index(stops_gdf):
    spatial_idx = index.Index()
    for i, row in stops_gdf.iterrows():
        spatial_idx.insert(i, row.geometry.bounds)
    return spatial_idx

def find_nearest_stops(user_location, stops_gdf, spatial_idx, radius_km=1.0):
    cache_key = f"nearest_stops:{user_location[0]}_{user_location[1]}_{radius_km}"
    if redis_client.exists(cache_key):
        return json.loads(redis_client.get(cache_key))
    
    user_point = Point(user_location[1], user_location[0])
    possible_matches = list(spatial_idx.intersection(user_point.buffer(radius_km / 111).bounds))
    nearby_stops = stops_gdf.iloc[possible_matches].to_dict()
    
    redis_client.set(cache_key, json.dumps(nearby_stops))
    return nearby_stops

# Reusable Query Functions
def get_next_trips(gtfs_data, stop_id, max_results=5):
    stop_times = pd.DataFrame(gtfs_data["stop_times"])
    trips = pd.DataFrame(gtfs_data["trips"])
    upcoming = stop_times[stop_times["stop_id"] == stop_id].sort_values("departure_time").head(max_results)
    upcoming = upcoming.merge(trips, on="trip_id", how="left")
    return upcoming[["trip_id", "route_id", "departure_time", "trip_headsign"]].to_dict(orient="records")

def search_routes_by_name(gtfs_data, route_name):
    routes = pd.DataFrame(gtfs_data["routes"])
    matched = routes[routes["route_long_name"].str.contains(route_name, case=False, na=False)]
    return matched[["route_id", "route_long_name", "route_type"]].to_dict(orient="records")

def get_stop_coordinates(gtfs_data, stop_id):
    stops = pd.DataFrame(gtfs_data["stops"])
    stop = stops[stops["stop_id"] == stop_id]
    if stop.empty:
        return None
    return {
        "stop_id": stop_id,
        "stop_name": stop["stop_name"].values[0],
        "latitude": stop["stop_lat"].values[0],
        "longitude": stop["stop_lon"].values[0]
    }

def calculate_path(gtfs_data, start_stop, end_stop):
    """Finds a direct or single-transfer path between two stops."""
    cache_key = f"path:{start_stop}:{end_stop}"
    if redis_client.exists(cache_key):
        return json.loads(redis_client.get(cache_key))
    
    stop_times = pd.DataFrame(gtfs_data["stop_times"])
    trips = pd.DataFrame(gtfs_data["trips"])

    start_df = stop_times[stop_times["stop_id"] == start_stop][["trip_id", "stop_sequence", "departure_time"]]
    end_df = stop_times[stop_times["stop_id"] == end_stop][["trip_id", "stop_sequence", "departure_time"]]

    direct = start_df.merge(end_df, on="trip_id", suffixes=("_start", "_end"))
    direct = direct[direct["stop_sequence_start"] < direct["stop_sequence_end"]]

    if not direct.empty:
        best = direct.sort_values("departure_time_start").iloc[0]
        result = {
            "trip_type": "direct",
            "trip_id": best["trip_id"],
            "departure_time": best["departure_time_start"],
            "arrival_time": best["departure_time_end"]
        }
        redis_client.set(cache_key, json.dumps(result))
        return result

    # Try 1-transfer: start → transfer → end
    transfer_df = stop_times[["trip_id", "stop_id", "stop_sequence", "departure_time"]]
    merged = start_df.merge(transfer_df, on="trip_id")
    merged = merged[merged["stop_sequence"] > merged["stop_sequence_start"]]
    transfer_stops = merged["stop_id"].unique()

    possible_second_legs = end_df[end_df["stop_id"].isin(transfer_stops)]
    if possible_second_legs.empty:
        redis_client.set(cache_key, json.dumps(None))
        return None

    second_leg = possible_second_legs.merge(transfer_df, on="stop_id", suffixes=("_end", "_transfer"))
    second_leg = second_leg[second_leg["stop_sequence_transfer"] < second_leg["stop_sequence_end"]]

    if not second_leg.empty:
        transfer = second_leg.iloc[0]
        result = {
            "trip_type": "1_transfer",
            "transfer_stop_id": transfer["stop_id"],
            "first_trip_id": transfer["trip_id_transfer"],
            "second_trip_id": transfer["trip_id_end"],
            "transfer_departure": transfer["departure_time_transfer"],
            "arrival_time": transfer["departure_time_end"]
        }
        redis_client.set(cache_key, json.dumps(result))
        return result

    redis_client.set(cache_key, json.dumps(None))
    return None

# Extra Utility Functions
def get_trip_stops(gtfs_data, trip_id):
    stop_times = pd.DataFrame(gtfs_data["stop_times"])
    stops = pd.DataFrame(gtfs_data["stops"])
    trip_stops = stop_times[stop_times["trip_id"] == trip_id].sort_values("stop_sequence")
    return trip_stops.merge(stops, on="stop_id")[["stop_id", "stop_name", "departure_time"]].to_dict(orient="records")

def get_routes_by_stop(gtfs_data, stop_id):
    stop_times = pd.DataFrame(gtfs_data["stop_times"])
    trips = pd.DataFrame(gtfs_data["trips"])
    routes = pd.DataFrame(gtfs_data["routes"])
    trip_ids = stop_times[stop_times["stop_id"] == stop_id]["trip_id"].unique()
    routes_join = trips[trips["trip_id"].isin(trip_ids)].merge(routes, on="route_id")
    return routes_join[["route_id", "route_long_name", "route_type"]].drop_duplicates().to_dict(orient="records")

# Load & Index on module import
gtfs_data = load_gtfs_data()
stops_gdf = get_stops_gdf(gtfs_data)
spatial_idx = build_spatial_index(stops_gdf)
