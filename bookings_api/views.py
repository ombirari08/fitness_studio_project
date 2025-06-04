# bookings_api/views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt # For POST requests without tokens
from django.utils import timezone
import pytz
from .models import _classes_data, _bookings_data, _next_class_id, _next_booking_id, \
                    FitnessClass, Booking, IST, UTC, populate_dummy_data # Import our "DB" and models
import logging

logger = logging.getLogger(__name__)

# Ensure dummy data is populated when the app starts
# A better place would be in AppConfig ready method, but for simplicity here:
populate_dummy_data()

# --- Utility functions for serializing our "models" ---
def serialize_class(class_instance, display_timezone=None):
    return class_instance.to_dict(display_timezone)

def serialize_booking(booking_instance):
    return booking_instance.to_dict()

# --- API Endpoints ---
@require_http_methods(["GET"])
def get_classes(request):
    """
    GET /api/classes
    Returns a list of all upcoming fitness classes.
    Optional query param: display_timezone (e.g., 'America/New_York')
    """
    display_timezone_str = request.GET.get('display_timezone', 'Asia/Kolkata') # Default to IST
    response_classes = []

    try:
        target_tz = pytz.timezone(display_timezone_str)
    except pytz.UnknownTimeZoneError:
        return JsonResponse({"detail": f"Invalid timezone: {display_timezone_str}"}, status=400)

    current_time_utc = timezone.now().astimezone(UTC) # Get current time in UTC

    for cls_instance in _classes_data:
        # Only show upcoming classes
        if cls_instance.date_time_utc < current_time_utc:
            continue
        response_classes.append(serialize_class(cls_instance, display_timezone_str))

    # Sort by date/time
    response_classes.sort(key=lambda x: x['date_time'])
    logger.info(f"Retrieved {len(response_classes)} classes for display in {display_timezone_str}.")
    return JsonResponse(response_classes, safe=False) # safe=False for list of dicts

@csrf_exempt # Disable CSRF token for this endpoint (for API simplicity)
@require_http_methods(["POST"])
def book_class(request):
    """
    POST /api/book
    Accepts a booking request (class_id, client_name, client_email).
    Validates slots and reduces them.
    """
    global _next_booking_id
    try:
        data = json.loads(request.body)
        class_id = data.get('class_id')
        client_name = data.get('client_name')
        client_email = data.get('client_email')

        # Basic input validation
        if not all([class_id, client_name, client_email]):
            logger.warning("Booking failed: Missing required fields.")
            return JsonResponse({"detail": "Missing class_id, client_name, or client_email."}, status=400)

        # Email validation (basic regex check could be added, or use a library)
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", client_email):
            logger.warning(f"Booking failed: Invalid email format for {client_email}.")
            return JsonResponse({"detail": "Invalid email format."}, status=400)

    except json.JSONDecodeError:
        logger.warning("Booking failed: Invalid JSON body.")
        return JsonResponse({"detail": "Invalid JSON body."}, status=400)


    # 1. Find the class
    found_class = None
    for cls_instance in _classes_data:
        if cls_instance.id == class_id:
            found_class = cls_instance
            break

    if not found_class:
        logger.warning(f"Booking failed: Class ID {class_id} not found.")
        return JsonResponse({"detail": "Class not found"}, status=404)

    # 2. Check for availability
    if found_class.available_slots <= 0:
        logger.warning(f"Booking failed for class {found_class.name}: No slots available.")
        return JsonResponse({"detail": "No available slots for this class"}, status=400)

    # 3. Prevent duplicate bookings by same client for the same class
    for booking_instance in _bookings_data:
        if booking_instance.class_id == class_id and booking_instance.client_email == client_email:
            logger.warning(f"Booking failed: Client {client_email} already booked class {found_class.name}.")
            return JsonResponse({"detail": "You have already booked this class."}, status=409)

    # 4. Reduce available slots (Directly modify the instance in our "DB")
    found_class.available_slots -= 1
    logger.info(f"Slot reduced for class {found_class.name}. New available: {found_class.available_slots}")


    # 5. Create the booking record
    new_booking_instance = Booking(
        id=_next_booking_id,
        class_id=class_id,
        client_name=client_name,
        client_email=client_email,
        booking_time_utc=timezone.now().astimezone(UTC), # Record booking time in UTC
        class_name=found_class.name
    )
    _bookings_data.append(new_booking_instance)
    _next_booking_id += 1
    logger.info(f"Successful booking by {client_email} for class {found_class.name} (ID: {class_id}). Booking ID: {new_booking_instance.id}")

    return JsonResponse(serialize_booking(new_booking_instance), status=201)

@require_http_methods(["GET"])
def get_bookings(request):
    """
    GET /api/bookings?client_email=<email>
    Returns all bookings made by a specific email address.
    """
    client_email = request.GET.get('client_email')

    if not client_email:
        logger.warning("Get bookings failed: client_email query parameter is missing.")
        return JsonResponse({"detail": "client_email query parameter is required."}, status=400)

    # Basic email validation for the query param
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", client_email):
        logger.warning(f"Get bookings failed: Invalid email format for query {client_email}.")
        return JsonResponse({"detail": "Invalid client_email format."}, status=400)


    client_bookings = [
        serialize_booking(b) for b in _bookings_data if b.client_email == client_email
    ]
    logger.info(f"Retrieved {len(client_bookings)} bookings for email: {client_email}.")
    return JsonResponse(client_bookings, safe=False)