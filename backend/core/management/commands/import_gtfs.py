import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import (
    Agency, Route, Stop, Trip, StopTime, Calendar,
    CalendarDate, Frequency, Shape
)

GTFS_DIR = os.path.join(settings.BASE_DIR, 'data', 'gtfs')

class Command(BaseCommand):
    help = 'Import GTFS data from .txt files'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting GTFS import...'))

        # self.import_agency()
        self.import_stops()
        self.import_routes()
        self.import_trips()
        self.import_stop_times()
        self.import_calendar()
        self.import_calendar_dates()
        self.import_frequencies()
        self.import_shapes()

        self.stdout.write(self.style.SUCCESS('GTFS import completed.'))

    def import_agency(self):
        path = os.path.join(GTFS_DIR, 'agency.txt')
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING('✘ agency.txt not found. Skipping.'))
            return
        Agency.objects.all().delete()
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Agency.objects.create(
                    agency_id=row['agency_id'],
                    name=row['agency_name'],
                    url=row['agency_url'],
                    timezone=row['agency_timezone'],
                    lang=row.get('agency_lang'),
                    phone=row.get('agency_phone'),
                    email=row.get('agency_email')
                )
        self.stdout.write(self.style.SUCCESS('✔ Agencies imported.'))

    def import_stops(self):
        path = os.path.join(GTFS_DIR, 'stops.txt')
        Stop.objects.all().delete()
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Stop.objects.create(
                    stop_id=row['stop_id'],
                    name=row['stop_name'],
                    lat=float(row['stop_lat']),
                    lon=float(row['stop_lon']),
                    code=row.get('stop_code')
                )
        self.stdout.write(self.style.SUCCESS('✔ Stops imported.'))

    def import_routes(self):
        path = os.path.join(GTFS_DIR, 'routes.txt')
        Route.objects.all().delete()
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Route.objects.create(
                    route_id=row['route_id'],
                    agency_id=row.get('agency_id'),
                    short_name=row.get('route_short_name'),
                    long_name=row.get('route_long_name'),
                    route_type=int(row.get('route_type', 0)),
                    color=row.get('route_color'),
                    text_color=row.get('route_text_color')
                )
        self.stdout.write(self.style.SUCCESS('✔ Routes imported.'))

    def import_trips(self):
        path = os.path.join(GTFS_DIR, 'trips.txt')
        Trip.objects.all().delete()
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Trip.objects.create(
                    trip_id=row['trip_id'],
                    route_id=row['route_id'],
                    service_id=row['service_id'],
                    headsign=row.get('trip_headsign'),
                    direction_id=int(row['direction_id']) if row.get('direction_id') else None
                )
        self.stdout.write(self.style.SUCCESS('✔ Trips imported.'))

    def import_stop_times(self):
        path = os.path.join(GTFS_DIR, 'stop_times.txt')
        StopTime.objects.all().delete()
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                StopTime.objects.create(
                    trip_id=row['trip_id'],
                    stop_id=row['stop_id'],
                    arrival_time=row['arrival_time'],
                    departure_time=row['departure_time'],
                    stop_sequence=int(row['stop_sequence'])
                )
        self.stdout.write(self.style.SUCCESS('✔ StopTimes imported.'))

    def import_calendar(self):
        path = os.path.join(GTFS_DIR, 'calendar.txt')
        Calendar.objects.all().delete()
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Calendar.objects.create(
                    service_id=row['service_id'],
                    monday=bool(int(row['monday'])),
                    tuesday=bool(int(row['tuesday'])),
                    wednesday=bool(int(row['wednesday'])),
                    thursday=bool(int(row['thursday'])),
                    friday=bool(int(row['friday'])),
                    saturday=bool(int(row['saturday'])),
                    sunday=bool(int(row['sunday'])),
                    start_date=row['start_date'],
                    end_date=row['end_date']
                )
        self.stdout.write(self.style.SUCCESS('✔ Calendar imported.'))

    def import_calendar_dates(self):
        path = os.path.join(GTFS_DIR, 'calendar_dates.txt')
        CalendarDate.objects.all().delete()
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                CalendarDate.objects.create(
                    service_id=row['service_id'],
                    date=row['date'],
                    exception_type=int(row['exception_type'])
                )
        self.stdout.write(self.style.SUCCESS('✔ Calendar Dates imported.'))

    def import_frequencies(self):
        path = os.path.join(GTFS_DIR, 'frequencies.txt')
        Frequency.objects.all().delete()
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Frequency.objects.create(
                    trip_id=row['trip_id'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    headway_secs=int(row['headway_secs'])
                )
        self.stdout.write(self.style.SUCCESS('✔ Frequencies imported.'))

    def import_shapes(self):
        path = os.path.join(GTFS_DIR, 'shapes.txt')
        Shape.objects.all().delete()
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Shape.objects.create(
                    shape_id=row['shape_id'],
                    lat=float(row['shape_pt_lat']),
                    lon=float(row['shape_pt_lon']),
                    sequence=int(row['shape_pt_sequence'])
                )
        self.stdout.write(self.style.SUCCESS('✔ Shapes imported.'))
