from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.utils.gtfs_utils import (
    find_nearest_stops,
    search_routes_by_name,
    get_next_trips,
    find_trip_plan_with_transfers,
    calculate_path,
    get_stop_coordinates,
    get_routes_by_stop,
    get_trip_stops,
    get_departure_board,
    gtfs_data, stops_gdf, spatial_idx
)

@csrf_exempt
def nearest_stops_view(request):
    """API to fetch nearby stops based on user location."""
    if request.method == "GET":
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        radius_km = float(request.GET.get("radius", 1.0))
        stops = find_nearest_stops((lat, lon), stops_gdf, spatial_idx, radius_km)
        return JsonResponse({"nearest_stops": stops})

@csrf_exempt
def route_search_view(request):
    """API to search for routes by name."""
    if request.method == "GET":
        route_name = request.GET.get("route_name")
        routes = search_routes_by_name(gtfs_data, route_name)
        return JsonResponse({"routes": routes})

@csrf_exempt
def next_trips_view(request):
    """API to fetch upcoming trips from a stop."""
    if request.method == "GET":
        stop_id = request.GET.get("stop_id")
        trips = get_next_trips(gtfs_data, stop_id)
        return JsonResponse({"next_trips": trips})

@csrf_exempt
def calculate_path_view(request):
    """API to compute the best transit path from A to B."""
    if request.method == "GET":
        start_stop = request.GET.get('start_stop')
        end_stop = request.GET.get('end_stop')
        time = request.GET.get('time', "08:00:00")  # Optional

        if not start_stop or not end_stop:
            return JsonResponse({"error": "Missing start_stop or end_stop"}, status=400)

        path = find_trip_plan_with_transfers(start_stop, end_stop, current_time_str=time)
        if not path:
            return JsonResponse({"message": "No path found"}, status=404)

        return JsonResponse({"path": path})

@csrf_exempt
def stop_coordinates_view(request):
    """API to fetch stop coordinates."""
    if request.method == "GET":
        stop_id = request.GET.get("stop_id")
        coords = get_stop_coordinates(gtfs_data, stop_id)
        return JsonResponse({"stop_coordinates": coords})

@csrf_exempt
def routes_by_stop_view(request):
    """API to list all routes serving a stop."""
    if request.method == "GET":
        stop_id = request.GET.get("stop_id")
        routes = get_routes_by_stop(gtfs_data, stop_id)
        return JsonResponse({"routes_by_stop": routes})

@csrf_exempt
def trip_stops_view(request):
    """API to fetch all stops along a trip."""
    if request.method == "GET":
        trip_id = request.GET.get("trip_id")
        stops = get_trip_stops(gtfs_data, trip_id)
        return JsonResponse({"trip_stops": stops})

@csrf_exempt
def departure_board_view(request):
    """API for upcoming departures at a stop."""
    if request.method == "GET":
        stop_id = request.GET.get("stop_id")
        time_window = int(request.GET.get("time_window", 30))
        departures = get_departure_board(gtfs_data, stop_id, time_window)
        return JsonResponse({"departure_board": departures})


# Create your views here.
