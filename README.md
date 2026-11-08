# Hospital Management System

A Django-based hospital appointment management system for patients and staff. Patients can register, log in, view available appointment slots, book appointments, and cancel appointments. Staff users can manage appointment schedules, patients, and appointment statuses from a protected dashboard.

## Features

- Patient registration and login using email
- Patient dashboard with upcoming appointment summary
- View available appointment slots
- Book appointments with a reason for visit
- Cancel appointments and release the slot for reuse
- Staff dashboard with patient, appointment, and slot statistics
- Staff schedule management
- Staff patient search and detail pages
- Staff appointment filtering by patient details, status, and date
- Appointment status updates: Confirmed, Completed, Cancelled
- Duplicate slot protection for the same date and time

## Tech Stack

- Python
- Django
- SQLite
- HTML templates
- CSS and JavaScript
- Gunicorn for production server startup

## Project Structure
Hospital Management system/
|-- appointments/
|   |-- migrations/
|   |-- static/
|   |   `-- appointments/
|   |       |-- css/
|   |       `-- js/
|   |-- templates/
|   |   `-- appointments/
|   |-- admin.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- urls.py
|   `-- views.py
|-- hospital_scheduler/
|   |-- asgi.py
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- manage.py
|-- Procfile
|-- requirements.txt
`-- README.md

## Main Models

### Patient
Stores patient profile details linked to Django's built-in `User` model.

### Schedule
Stores appointment date and time slots. Each date and time combination is unique.

### Appointment
Stores patient bookings, reason for visit, appointment status, and creation time.

## Pages and Routes
| Page | URL | Access |
| --- | --- | --- |
| Home | `/` | Public |
| About | `/about/` | Public |
| Contact | `/contact/` | Public |
| Register | `/register/` | Public |
| Login | `/login/` | Public |
| Patient Dashboard | `/dashboard/` | Patient |
| Available Slots | `/slots/` | Patient |
| Book Appointment | `/slots/<schedule_id>/book/` | Patient |
| My Appointments | `/appointments/` | Patient |
| Cancel Appointment | `/appointments/<appointment_id>/cancel/` | Patient |
| Staff Dashboard | `/staff/dashboard/` | Staff |
| Manage Schedules | `/staff/schedules/` | Staff |
| Add Schedule | `/staff/schedules/add/` | Staff |
| Edit Schedule | `/staff/schedules/<schedule_id>/edit/` | Staff |
| Manage Patients | `/staff/patients/` | Staff |
| Patient Details | `/staff/patients/<patient_id>/` | Staff |
| Manage Appointments | `/staff/appointments/` | Staff |
| Django Admin | `/admin/` | Admin |

## Setup Instructions
### 1. Clone the Repository
git clone https://github.com/PranathiR73/MediSchedule.git
cd hospital-management-system

### 2. Create a Virtual Environment
On Windows:
python -m venv venv
venv\Scripts\activate

On macOS or Linux:
python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt


### 4. Apply Database Migrations
python manage.py migrate


### 5. Create a Staff/Admin User
python manage.py createsuperuser
Use this account to access the Django admin panel and staff dashboard.

### 6. Run the Development Server
python manage.py runserver

Open the app in your browser:
http://127.0.0.1:8000/

## Staff Access
The staff dashboard is available only to users with `is_staff=True`.
To make a user staff from the Django admin:
1. Log in at `/admin/`.
2. Open the user record.
3. Enable `Staff status`.
4. Save the user.

## Useful Commands
Run migrations:python manage.py migrate
Create new migrations after model changes: python manage.py makemigrations
Run the development server:python manage.py runserver
Create an admin user:python manage.py createsuperuser
Collect static files for production:python manage.py runserver
