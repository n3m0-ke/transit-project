from django.urls import path, include
from core import views

urlpatterns = [
    path("nearest_stops/", views.get_nearby_stops, name="nearest_stops"),
    path("search_routes/", views.route_search, name="search_routes"),
    path("next_trips/", views.trip_stops, name="next_trips"),  # Assuming this is meant for trip_stops
    path("calculate_path/", views.find_path, name="calculate_path"),
    path("stop_coordinates/", views.stop_coordinates, name="stop_coordinates"),
    path("routes_by_stop/", views.stop_routes, name="routes_by_stop"),
    path("trip_stops/", views.trip_stops, name="trip_stops"),  # Duplicate?
    path("departure_board/", views.stop_board, name="departure_board"),

    #authentication
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("auth/social/", include("allauth.socialaccount.urls")),
]
