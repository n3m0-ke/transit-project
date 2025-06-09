from django.db import models

class Agency(models.Model):
    agency_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=255)
    url = models.URLField()
    timezone = models.CharField(max_length=64)
    lang = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=64, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    route_id = models.CharField(max_length=64, primary_key=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    short_name = models.CharField(max_length=64)
    long_name = models.CharField(max_length=255)
    route_type = models.IntegerField()
    color = models.CharField(max_length=6, null=True, blank=True)
    text_color = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return f"{self.short_name} - {self.long_name}"


class Stop(models.Model):
    stop_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()
    code = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name


class Trip(models.Model):
    trip_id = models.CharField(max_length=64, primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    service_id = models.CharField(max_length=64)
    headsign = models.CharField(max_length=255, null=True, blank=True)
    direction_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.trip_id


class StopTime(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    stop_sequence = models.IntegerField()

    class Meta:
        unique_together = ('trip', 'stop_sequence')
        ordering = ['trip', 'stop_sequence']


class Calendar(models.Model):
    service_id = models.CharField(max_length=64, primary_key=True)
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField()


class CalendarDate(models.Model):
    service_id = models.CharField(max_length=64)
    date = models.DateField()
    exception_type = models.IntegerField()  # 1 = Added, 2 = Removed

    class Meta:
        unique_together = ('service_id', 'date')


class Frequency(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    headway_secs = models.IntegerField()


class Shape(models.Model):
    shape_id = models.CharField(max_length=64)
    lat = models.FloatField()
    lon = models.FloatField()
    sequence = models.IntegerField()

    class Meta:
        unique_together = ('shape_id', 'sequence')
