# 🚀 Fitness Studio Booking API (Django)

Namaste! Welcome to the Fitness Studio Booking API, a simple yet effective backend for managing fitness classes and client bookings. I whipped this up using Django, and it's designed to give you a quick look at how you can handle class listings and client bookings efficiently. While the data lives happily in memory for now (so it resets with every server restart – just like my energy levels after a good workout!), it showcases the core logic beautifully.

## ✨ What This API Can Do

Here's a peek at the cool stuff you can achieve with this API:

* **Browse Classes:** Get a neat list of all upcoming fitness classes. You'll see who's teaching (our amazing instructors!), when it's happening, and how many spots are left. The best part? You can even view class times adjusted to different timezones – super handy for our global fitness community!
* **Book Your Spot:** Clients can easily snag a spot in their favorite class. The API intelligently checks for available slots and ensures no one double-books the same class. No overbooking chaos here!
* **Track Your Bookings:** Want to see what classes you've signed up for? Just use your email, and the API will fetch all your past bookings.
* **Smart Time Handling:** Classes are originally set in Indian Standard Time (IST), but everything's stored internally in Coordinated Universal Time (UTC) for accuracy. When you ask for class times, you can pick any timezone, and the API will smartly adjust it for you.
* **Friendly Error Messages:** If something goes wrong (like trying to book a full class or typing in the wrong class ID), the API gives clear, helpful messages so you know exactly what happened.
* **Basic Logging:** I've added some basic logs to the console so you can see what's happening behind the scenes as requests come in.

## 🛠️ Getting Started: Your Local Setup

Ready to get this API up and running on your machine? It's pretty straightforward, almost like setting up your gym bag for a class!

1.  **Grab the Code:**
    First things first, let's get the project files.
    ```bash
    git clone [https://github.com/your-username/fitness_studio_project.git](https://github.com/your-username/fitness_studio_project.git)
    cd fitness_studio_project
    ```
    *(Remember to replace the GitHub URL with your actual repository link if you upload it to GitHub.)*

2.  **Set Up Your Playground (Virtual Environment):**
    It's always a good practice to work in a virtual environment to keep your project dependencies tidy.
    ```bash
    python -m venv venv
    # On Windows, activate it like this:
    .\venv\Scripts\activate
    # On macOS/Linux, use this:
    source venv/bin/activate
    ```

3.  **Install the Essentials:**
    Now, let's get all the necessary Python packages installed.
    ```bash
    pip install -r requirements.txt
    ```
    *(If you don't have `requirements.txt` yet, create it after step 4 by using `pip freeze > requirements.txt`)*

4.  **Django Housekeeping (Migrations):**
    Although our API data is in memory, Django likes to set up its own little `db.sqlite3` file for its internal bits. This command handles that.
    ```bash
    python manage.py migrate
    ```

5.  **Fire Up the Server!**
    And just like that, your API is ready to serve!
    ```bash
    python manage.py runserver
    ```
    You'll see messages in your console confirming that some dummy class data (our "seed" data) has been populated – think of it as the initial class schedule for the studio. The API will be humming along at `http://127.0.0.1:8000/`.

## 💻 API Endpoints: How to Interact

All our API magic happens under the `/api/` prefix.

### 1. `GET /api/classes/`

Curious about what classes are available? This is your go-to endpoint!

* **Method:** `GET`
* **URL:** `http://127.0.0.1:8000/api/classes/`
* **Optional Query Parameter:**
    * `display_timezone`: Want to see class times in your local zone? Just specify the timezone (e.g., `'America/New_York'`, `'Europe/London'`, or even `Asia/Kolkata` for our local flavor!). It defaults to `Asia/Kolkata` (IST) if you don't provide one.
* **Try it with `curl`:**
    ```bash
    curl [http://127.0.0.1:8000/api/classes/](http://127.0.0.1:8000/api/classes/)
    # Or for a specific timezone:
    curl "[http://127.0.0.1:8000/api/classes/?display_timezone=America/New_York](http://127.0.0.1:8000/api/classes/?display_timezone=America/New_York)"
    ```
* **What you'll get (Example JSON Response):**
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

Ready to book a class? This is where the action happens!

* **Method:** `POST`
* **URL:** `http://127.0.0.1:8000/api/book/`
* **What to Send (JSON Request Body):**
    ```json
    {
        "class_id": 1,
        "client_name": "Rohan Patel",
        "client_email": "rohan.patel@example.com"
    }
    ```
    * `class_id`: The ID of the class to book (obtain from `GET /api/classes/`).
    * `client_name`: Your name (or your client's name).
    * `client_email`: Your email, so we know who's booking (and it's validated, don't worry!).
* **Try it with `curl`:**
    ```bash
    curl -X POST \
         -H "Content-Type: application/json" \
         -d '{"class_id": 1, "client_name": "Rohan Patel", "client_email": "rohan.patel@example.com"}' \
         [http://127.0.0.1:8000/api/book/](http://127.0.0.1:8000/api/book/)
    ```
* **What you'll get (Success - Status 201 Created):**
    ```json
    {
        "id": 1,
        "class_id": 1,
        "client_name": "Rohan Patel",
        "client_email": "rohan.patel@example.com",
        "booking_time": "2025-06-04T18:00:00Z", # This is in UTC!
        "class_name": "Morning Yoga"
    }
    ```
* **Possible Error Responses (Just so you know!):**
    * `400 Bad Request`: If you miss a field, provide an invalid email, or try to book a class with no slots left.
    * `404 Not Found`: If that `class_id` doesn't exist.
    * `409 Conflict`: If `rohan.patel@example.com` tries to book the *same* class again!

### 3. `GET /api/bookings/`

Curious about all the classes a particular client has booked?

* **Method:** `GET`
* **URL:** `http://127.0.0.1:8000/api/bookings/`
* **Required Query Parameter:**
    * `client_email`: Just provide the email address, and we'll fetch their bookings.
* **Try it with `curl`:**
    ```bash
    curl "[http://127.0.0.1:8000/api/bookings/?client_email=rohan.patel@example.com](http://127.0.0.1:8000/api/bookings/?client_email=rohan.patel@example.com)"
    ```
* **What you'll get (Example JSON Response):**
    ```json
    [
        {
            "id": 1,
            "class_id": 1,
            "client_name": "Rohan Patel",
            "client_email": "rohan.patel@example.com",
            "booking_time": "2025-06-04T18:00:00Z",
            "class_name": "Morning Yoga"
        }
    ]
    ```
    * You'll get an empty list `[]` if no bookings are found for that email – simple as that!

---

Thanks for checking out this little fitness studio project! If you have any questions or just want to chat about code, feel free to reach out! Happy coding!
