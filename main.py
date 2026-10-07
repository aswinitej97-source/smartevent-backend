from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models
import schemas
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartEvent API")

security = HTTPBearer()


# ---------------- HOME ----------------

@app.get("/")
def home():
    return {"message": "SmartEvent Backend is running"}


# ---------------- AUTH REGISTER ----------------

@app.post(
    "/auth/register",
    response_model=schemas.UserResponse,
    status_code=201
)
def register_user(
    user: schemas.UserRegister,
    db: Session = Depends(get_db)
):
    existing_email = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    existing_username = (
        db.query(models.User)
        .filter(models.User.username == user.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ---------------- AUTH LOGIN ----------------

@app.post("/auth/login")
def login_user(
    user: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    db_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if not db_user or not verify_password(
        user.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {
            "sub": str(db_user.id),
            "email": db_user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------------- CURRENT USER ----------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ---------------- PROFILE ----------------

@app.get(
    "/auth/profile",
    response_model=schemas.UserResponse
)
def get_profile(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


# ---------------- CREATE EVENT ----------------

@app.post(
    "/events",
    response_model=schemas.EventResponse,
    status_code=201
)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_event = models.Event(
        title=event.title,
        description=event.description,
        category=event.category,
        location=event.location,
        event_date=event.event_date,
        ticket_price=event.ticket_price,
        banner_image=event.banner_image
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


# ---------------- GET / FILTER EVENTS ----------------

@app.get(
    "/events",
    response_model=list[schemas.EventResponse]
)
def get_events(
    category: str = None,
    location: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Event)

    if category:
        query = query.filter(
            models.Event.category == category
        )

    if location:
        query = query.filter(
            models.Event.location == location
        )

    return query.all()


# ---------------- GET EVENT BY ID ----------------

@app.get(
    "/events/{event_id}",
    response_model=schemas.EventResponse
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = (
        db.query(models.Event)
        .filter(models.Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return event
# ---------------- CREATE BOOKING ----------------

@app.post(
    "/bookings",
    response_model=schemas.BookingResponse,
    status_code=201
)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    event = (
        db.query(models.Event)
        .filter(models.Event.id == booking.event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if booking.ticket_quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Ticket quantity must be greater than 0"
        )

    total_price = event.ticket_price * booking.ticket_quantity

    new_booking = models.Booking(
        user_id=current_user.id,
        event_id=booking.event_id,
        ticket_quantity=booking.ticket_quantity,
        total_price=total_price,
        booking_status="CONFIRMED"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking
# ---------------- CREATE BOOKING ----------------

@app.post(
    "/bookings",
    response_model=schemas.BookingResponse,
    status_code=201
)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    event = (
        db.query(models.Event)
        .filter(models.Event.id == booking.event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if booking.ticket_quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Ticket quantity must be greater than 0"
        )

    total_price = event.ticket_price * booking.ticket_quantity

    new_booking = models.Booking(
        user_id=current_user.id,
        event_id=booking.event_id,
        ticket_quantity=booking.ticket_quantity,
        total_price=total_price,
        booking_status="CONFIRMED"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking
# ---------------- GENERATE TICKET ----------------

@app.post("/bookings/{booking_id}/ticket")
def generate_ticket(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    import uuid

    booking = (
        db.query(models.Booking)
        .filter(
            models.Booking.id == booking_id,
            models.Booking.user_id == current_user.id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.booking_status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Cancelled booking cannot generate ticket"
        )

    existing_ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.booking_id == booking.id)
        .first()
    )

    if existing_ticket:
        return existing_ticket

    ticket = models.Ticket(
        booking_id=booking.id,
        ticket_code=str(uuid.uuid4()),
        qr_code_url=None
    )

    notification = models.Notification(
        user_id=current_user.id,
        title="Ticket Generated",
        message=f"Your ticket for booking {booking.id} is ready.",
        type="BOOKING",
        is_read=False
    )

    db.add(ticket)
    db.add(notification)
    db.commit()
    db.refresh(ticket)

    return ticket

# ---------------- MY BOOKINGS ----------------

@app.get(
    "/bookings/my",
    response_model=list[schemas.BookingResponse]
)
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.Booking)
        .filter(models.Booking.user_id == current_user.id)
        .all()
    )


# ---------------- CANCEL BOOKING ----------------

@app.put(
    "/bookings/{booking_id}/cancel",
    response_model=schemas.BookingResponse
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = (
        db.query(models.Booking)
        .filter(
            models.Booking.id == booking_id,
            models.Booking.user_id == current_user.id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    booking.booking_status = "CANCELLED"

    db.commit()
    db.refresh(booking)

    return booking


# ---------------- MY TICKETS ----------------

@app.get("/tickets/my")
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tickets = (
        db.query(models.Ticket)
        .join(
            models.Booking,
            models.Ticket.booking_id == models.Booking.id
        )
        .filter(models.Booking.user_id == current_user.id)
        .all()
    )

    return tickets


# ---------------- NOTIFICATIONS ----------------

@app.get("/notifications")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .all()
    )


# ---------------- MARK NOTIFICATION READ ----------------

@app.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    notification = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == current_user.id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification