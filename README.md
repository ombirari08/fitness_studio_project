# Booking API for a fictional fitness studio using Python

This is a simple RESTful API for a fictional fitness studio, built with Django. It allows clients to view available classes and book spots. The data is stored entirely in memory for simplicity, resetting with each server restart.

## Features

* **View Classes:** Get a list of all upcoming fitness classes with details like name, date/time, instructor, and available slots. Supports timezone conversion for display.
* **Book Class:** Book a spot in a specific class, validating slot availability and preventing duplicate bookings by the same client for the same class.
* **View Bookings:** Retrieve all bookings made by a specific client email address.
* **Timezone Management:** Classes are created in IST, stored internally in UTC, and can be displayed in a client-specified timezone.
* **Error Handling:** Provides informative error responses for cases like class not found, no available slots, invalid input, or duplicate bookings.
* **Basic Logging:** Logs API interactions and key events to the console.

## Technical Stack

* **Python:** 3.9+ recommended
* **Framework:** Django 5.x
* **Timezones:** `pytz` library for robust timezone handling.
* **Data Storage:** In-memory Python lists and objects (data resets on server restart).

## Setup Instructions

Follow these steps to get the API running on your local machine:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/fitness_studio_project.git](https://github.com/your-username/fitness_studio_project.git)
    cd fitness_studio_project
    ```
    *(Replace `https://github.com/your-username/fitness_studio_project.git` with your actual repo URL if you upload it to GitHub.)*

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(If `requirements.txt` is missing, you can create it after step 4 by running `pip freeze > requirements.txt`)*

4.  **Run Django Migrations (Optional, for `db.sqlite3` creation):**
    Although this project uses in-memory data for the API, Django requires a database for its built-in features (like admin, sessions). This command will create the `db.sqlite3` file and necessary tables.
    ```bash
    python manage.py migrate
    ```

5.  **Run the Django Development Server:**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`. You will see console output indicating that dummy data for classes has been populated on startup.

## API Endpoints

All API endpoints are prefixed with `/api/`.

### 1. `GET /api/classes/`

Returns a list of all upcoming fitness classes.

* **Method:** `GET`
* **URL:** `http://127.0.0.1:8000/api/classes/`
* **Query Parameters:**
    * `display_timezone` (Optional): A string representing the timezone to display class times in (e.g., `'America/New_York'`, `'Europe/London'`, `'Asia/Kolkata'`). Defaults to `'Asia/Kolkata'` (IST).
* **Sample cURL Request:**
    ```bash
    curl [http://127.0.0.1:8000/api/classes/](http://127.0.0.1:8000/api/classes/)
    # Or for a specific timezone:
    curl "[http://127.0.0.1:8000/api/classes/?display_timezone=America/New_York](http://127.0.0.1:8000/api/classes/?display_timezone=America/New_York)"
    ```
* **Sample JSON Response (Example):**
    ```json
    [
        {
            "id": 1,
            "name": "Morning Yoga",
            "instructor": "Priya Sharma",
            "total_slots": 15,
            "available_slots": 15,
            "date_time": "2025-06-05T07:00:00+05:30",
            "date_time_display_tz": "IST"
        },
        {
            "id": 2,
            "name": "Zumba Dance",
            "instructor": "Rahul Singh",
            "total_slots": 20,
            "available_slots": 20,
            "date_time": "2025-06-05T18:30:00+05:30",
            "date_time_display_tz": "IST"
        }
    ]
    ```

### 2. `POST /api/book/`

Accepts a booking request and attempts to book a spot in a class.

* **Method:** `POST`
* **URL:** `http://127.0.0.1:8000/api/book/`
* **Request Body (JSON):**
    ```json
    {
        "class_id": 1,
        "client_name": "Alice Wonderland",
        "client_email": "alice@example.com"
    }
    ```
    * `class_id`: The ID of the class to book (obtain from `GET /api/classes/`).
    * `client_name`: The name of the client.
    * `client_email`: The email of the client (must be a valid email format).
* **Sample cURL Request:**
    ```bash
    curl -X POST \
         -H "Content-Type: application/json" \
         -d '{"class_id": 1, "client_name": "Alice Wonderland", "client_email": "alice@example.com"}' \
         [http://127.0.0.1:8000/api/book/](http://127.0.0.1:8000/api/book/)
    ```
* **Sample JSON Response (Success - Status 201 Created):**
    ```json
    {
        "id": 1,
        "class_id": 1,
        "client_name": "Alice Wonderland",
        "client_email": "alice@example.com",
        "booking_time": "2025-06-04T18:00:00Z", # UTC time
        "class_name": "Morning Yoga"
    }
    ```
* **Error Responses (Examples):**
    * **400 Bad Request:**
        ```json
        {"detail": "Missing class_id, client_name, or client_email."}
        {"detail": "Invalid email format."}
        {"detail": "No available slots for this class"}
        ```
    * **404 Not Found:**
        ```json
        {"detail": "Class not found"}
        ```
    * **409 Conflict:**
        ```json
        {"detail": "You have already booked this class."}
        ```

### 3. `GET /api/bookings/`

Returns all bookings made by a specific client email address.

* **Method:** `GET`
* **URL:** `http://127.0.0.1:8000/api/bookings/`
* **Query Parameters:**
    * `client_email` (Required): The email address of the client whose bookings you want to retrieve.
* **Sample cURL Request:**
    ```bash
    curl "[http://127.0.0.1:8000/api/bookings/?client_email=alice@example.com](http://127.0.0.1:8000/api/bookings/?client_email=alice@example.com)"
    ```
* **Sample JSON Response (Example):**
    ```json
    [
        {
            "id": 1,
            "class_id": 1,
            "client_name": "Alice Wonderland",
            "client_email": "alice@example.com",
            "booking_time": "2025-06-04T18:00:00Z",
            "class_name": "Morning Yoga"
        }
    ]
    ```
    * Returns an empty list `[]` if no bookings are found for the email.
* **Error Responses (Examples):**
    * **400 Bad Request:**
        ```json
        {"detail": "client_email query parameter is required."}
        {"detail": "Invalid client_email format."}
        ```


---

This README, combined with the structured code, should provide a complete deliverable for your assignment.
