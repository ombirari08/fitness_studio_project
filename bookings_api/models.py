# bookings_api/models.py

from django.db import models
from django.utils import timezone
import pytz

# Define IST timezone for consistency
IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.utc

# --- In-Memory Data Stores ---
_classes_data = []
_bookings_data = []
_next_class_id = 1
_next_booking_id = 1

class FitnessClass:
    def __init__(self, id, name, instructor, total_slots, date_time_utc, available_slots):
        self.id = id
        self.name = name
        self.instructor = instructor
        self.total_slots = total_slots
        self.date_time_utc = date_time_utc
        self.available_slots = available_slots

    def to_dict(self, display_timezone=None):
        display_dt = self.date_time_utc
        if display_timezone:
            try:
                target_tz = pytz.timezone(display_timezone)
                display_dt = self.date_time_utc.astimezone(target_tz)
            except pytz.UnknownTimeZoneError:
                display_dt = self.date_time_utc.astimezone(IST) # Fallback if invalid TZ
        else:
            display_dt = self.date_time_utc.astimezone(IST) # Default display in IST

        return {
            "id": self.id,
            "name": self.name,
            "instructor": self.instructor,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "date_time": display_dt.isoformat(),
            "date_time_display_tz": display_dt.tzname()
        }

class Booking:
    def __init__(self, id, class_id, client_name, client_email, booking_time_utc, class_name):
        self.id = id
        self.class_id = class_id
        self.client_name = client_name
        self.client_email = client_email
        self.booking_time_utc = booking_time_utc
        self.class_name = class_name

    def to_dict(self):
        return {
            "id": self.id,
            "class_id": self.class_id,
            "client_name": self.client_name,
            "client_email": self.client_email,
            "booking_time": self.booking_time_utc.isoformat(),
            "class_name": self.class_name
        }

def populate_dummy_data():
    global _next_class_id
    global _classes_data

    if not _classes_data: # Only populate if empty
        def _create_class_entry(name, instructor, total_slots, date_time_str_ist):
            global _next_class_id
            # 1. Parse the string into a naive datetime object
            naive_dt_obj = timezone.datetime.strptime(date_time_str_ist, "%Y-%m-%d %H:%M")
            
            # 2. Localize the naive datetime to IST using pytz
            # This makes dt_obj_ist_aware a timezone-aware datetime object (e.g., 2025-06-06 07:00:00+05:30)
            dt_obj_ist_aware = IST.localize(naive_dt_obj)
            
            # 3. Directly convert the IST-aware datetime to UTC for internal storage
            # No need for timezone.make_aware() here as dt_obj_ist_aware is already aware.
            dt_obj_utc = dt_obj_ist_aware.astimezone(UTC)

            class_instance = FitnessClass(
                id=_next_class_id,
                name=name,
                instructor=instructor,
                total_slots=total_slots,
                available_slots=total_slots,
                date_time_utc=dt_obj_utc # Store as UTC
            )
            _classes_data.append(class_instance)
            print(f"Added class: {name} at {date_time_str_ist} (IST) -> Stored as {dt_obj_utc} (UTC)")
            _next_class_id += 1

        _create_class_entry("Morning Yoga", "Priya Sharma", 15, "2025-06-06 07:00")
        _create_class_entry("Zumba Dance", "Rahul Singh", 20, "2025-06-06 18:30")
        _create_class_entry("HIIT Blast", "Anjali Verma", 10, "2025-06-07 08:00")
        _create_class_entry("Evening Yoga", "Priya Sharma", 12, "2025-06-07 19:00")

    print("Dummy data population check completed.")