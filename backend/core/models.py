from django.db import models

class User(models.Model):
    """Stores user profile details."""
    id = models.UUIDField(primary_key=True, editable=False)
    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SavedRoute(models.Model):
    """Stores routes saved by users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    route_id = models.CharField(max_length=20)
    nickname = models.CharField(max_length=100)

class UserPreference(models.Model):
    """Stores user preferences (theme, home stop, etc.)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=False)
    home_stop_id = models.CharField(max_length=20, null=True, blank=True)

class TripHistory(models.Model):
    """Records past trips taken by users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip_id = models.CharField(max_length=20)
    stop_id = models.CharField(max_length=20)
    datetime = models.DateTimeField(auto_now_add=True)
