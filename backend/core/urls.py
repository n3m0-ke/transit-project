from django.urls import path
from core.views import (
    nearest_stops_view,
    route_search_view,
    next_trips_view,
    calculate_path_view,
    stop_coordinates_view,
    routes_by_stop_view,
    trip_stops_view,
    departure_board_view
)

urlpatterns = [
    path("nearest_stops/", nearest_stops_view, name="nearest_stops"),
    path("search_routes/", route_search_view, name="search_routes"),
    path("next_trips/", next_trips_view, name="next_trips"),
    path("calculate_path/", calculate_path_view, name="calculate_path"),
    path("stop_coordinates/", stop_coordinates_view, name="stop_coordinates"),
    path("routes_by_stop/", routes_by_stop_view, name="routes_by_stop"),
    path("trip_stops/", trip_stops_view, name="trip_stops"),
    path("departure_board/", departure_board_view, name="departure_board"),
]