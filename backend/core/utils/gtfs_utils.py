import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Define file paths
GTFS_DIR = "data/gtfs"
FILES = {
    "stops": "stops.txt",
    "routes": "routes.txt",
    "trips": "trips.txt",
    "stop_times": "stop_times.txt",
    "shapes": "shapes.txt"
}

# Load GTFS data as pandas DataFrames
def load_gtfs_data():
    """Loads GTFS files into Pandas DataFrames."""
    data = {}
    for key, filename in FILES.items():
        file_path = f"{GTFS_DIR}/{filename}"
        data[key] = pd.read_csv(file_path)
    return data

# Convert stops to GeoDataFrame for spatial indexing
def get_stops_gdf(gtfs_data):
    """Returns a GeoDataFrame of stops with spatial indexing."""
    stops_df = gtfs_data["stops"]
    stops_df["geometry"] = stops_df.apply(lambda row: Point(row["stop_lon"], row["stop_lat"]), axis=1)
    return gpd.GeoDataFrame(stops_df, geometry="geometry", crs="EPSG:4326")

# Find nearest stops
def find_nearest_stops(user_location, stops_gdf, radius_km=1.0):
    """Finds stops within a given radius (km) from user location."""
    user_point = Point(user_location[1], user_location[0])  # (lat, lon)
    buffer = user_point.buffer(radius_km / 111)  # Approximate degrees to km conversion
    return stops_gdf[stops_gdf["geometry"].within(buffer)]

# Get trip details for a route
def get_route_trips(gtfs_data, route_id):
    """Fetches trips associated with a given route."""
    return gtfs_data["trips"][gtfs_data["trips"]["route_id"] == route_id]

# Get stop times for a specific trip
def get_trip_stop_times(gtfs_data, trip_id):
    """Fetches stop times for a given trip ID."""
    return gtfs_data["stop_times"][gtfs_data["stop_times"]["trip_id"] == trip_id].sort_values("stop_sequence")

# Initialize GTFS data
gtfs_data = load_gtfs_data()
stops_gdf = get_stops_gdf(gtfs_data)

if __name__ == "__main__":
    # Example usage
    user_location = (-1.286389, 36.817223)  # Nairobi CBD
    nearby_stops = find_nearest_stops(user_location, stops_gdf)
    print(nearby_stops[["stop_id", "stop_name"]])