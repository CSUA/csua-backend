import datetime

from decouple import config
from django.core.cache import cache
from django.core.management.base import BaseCommand
from googleapiclient.discovery import build


class Command(BaseCommand):
    help = "Fetch Google Calendar events and cache them"

    def handle(self, *args, **kwargs):
        API_KEY = config("GOOGLE_CALENDAR_API_KEY")
        CALENDAR_ID = (
            "berkeley.edu_rv641pmt9o13qnh1ss4uib78bs@group.calendar.google.com"
        )

        service = build("calendar", "v3", developerKey=API_KEY)

        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(
                calendarId=CALENDAR_ID,
                timeMin=now,
                maxResults=50,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        cache.set("calendar_events", events, timeout=3600)  # Cache for 1 hour
        self.stdout.write(self.style.SUCCESS(f"Fetched {len(events)} events."))
