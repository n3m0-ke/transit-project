from django.urls import path, include
from dj_rest_auth.jwt_auth import get_refresh_view
from core import views
from core.social_login import GoogleLogin

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
    path("auth/social/google/", GoogleLogin.as_view(), name="google_login"),

    path("token/refresh/", get_refresh_view().as_view(), name='token_refresh'),

    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),  # Needed for social login

    #test protected route
    path("protected/", views.protected_view, name="protected_view"),
]
