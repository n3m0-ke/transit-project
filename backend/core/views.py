from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from core.utils.gtfs_utils import (
    load_gtfs_data,
    get_stops_gdf,
    build_spatial_index,
    find_nearest_stops,
    search_routes_by_name,
    get_trip_stops,
    get_routes_by_stop,
    get_departure_board,
    calculate_path,
    get_stop_coordinates,
)

# Load GTFS data once when server starts
gtfs_data = load_gtfs_data()
stops_gdf = get_stops_gdf(gtfs_data)
spatial_idx = build_spatial_index(stops_gdf)

@require_GET
def get_nearby_stops(request):
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        radius = float(request.GET.get("radius", 1.0))
        nearby = find_nearest_stops((lat, lon), stops_gdf, spatial_idx, radius_km=radius)
        return JsonResponse({"stops": nearby})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_GET
def route_search(request):
    try:
        query = request.GET.get("q", "")
        if not query:
            return JsonResponse({"error": "Missing query string"}, status=400)
        matches = search_routes_by_name(gtfs_data, query)
        return JsonResponse({"routes": matches})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_GET
def trip_stops(request):
    try:
        trip_id = request.GET.get("trip_id")
        if not trip_id:
            return JsonResponse({"error": "trip_id required"}, status=400)
        stops = get_trip_stops(gtfs_data, trip_id)
        return JsonResponse({"stops": stops})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_GET
def stop_routes(request):
    try:
        stop_id = request.GET.get("stop_id")
        if not stop_id:
            return JsonResponse({"error": "stop_id required"}, status=400)
        routes = get_routes_by_stop(gtfs_data, stop_id)
        return JsonResponse({"routes": routes})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_GET
def stop_board(request):
    try:
        stop_id = request.GET.get("stop_id")
        if not stop_id:
            return JsonResponse({"error": "stop_id required"}, status=400)
        board = get_departure_board(gtfs_data, stop_id)
        return JsonResponse({"departures": board})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_GET
def stop_coordinates(request):
    try:
        stop_id = request.GET.get("stop_id")
        if not stop_id:
            return JsonResponse({"error": "stop_id required"}, status=400)
        coords = get_stop_coordinates(gtfs_data, stop_id)
        return JsonResponse({"stop": coords})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_GET
def find_path(request):
    try:
        start = request.GET.get("start_stop")
        end = request.GET.get("end_stop")
        if not start or not end:
            return JsonResponse({"error": "start_stop and end_stop required"}, status=400)
        path = calculate_path(gtfs_data, start, end)
        return JsonResponse({"path": path})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({'message': f'Hello, {request.user.email}. You are authenticated!'})
