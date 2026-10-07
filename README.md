# SmartEvent – Event Discovery & Ticket Booking System

SmartEvent is a backend application developed using FastAPI for event discovery and ticket booking.

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT Authentication
- Bcrypt
- Uvicorn

## Features

### User Authentication
- User Registration
- User Login
- JWT Authentication
- Password Hashing
- Protected Routes
- User Profile

### Event Management
- Create Event
- Get All Events
- Filter Events by Category and Location
- Get Event by ID

### Booking Management
- Create Booking
- View My Bookings
- Cancel Booking
- Automatic Total Price Calculation

### Ticket Management
- Generate Ticket
- Unique Ticket Code
- View My Tickets

### Notifications
- View Notifications
- Mark Notification as Read

## Run the Project

Install dependencies:

pip install -r requirements.txt

Start the FastAPI server:

uvicorn main:app --reload

Open Swagger API documentation:

http://127.0.0.1:8000/docs

## API Testing

The APIs were tested using FastAPI Swagger UI.

## Project Status

Backend implementation completed and core APIs tested successfully.