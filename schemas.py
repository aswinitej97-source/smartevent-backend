from pydantic import BaseModel, EmailStr
from datetime import datetime


# ================= USER =================

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# ================= EVENT =================

class EventCreate(BaseModel):
    title: str
    description: str
    category: str
    location: str
    event_date: datetime
    ticket_price: float
    banner_image: str | None = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    category: str
    location: str
    event_date: datetime
    ticket_price: float
    banner_image: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# ================= BOOKING =================

class BookingCreate(BaseModel):
    event_id: int
    ticket_quantity: int


class BookingResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    ticket_quantity: int
    total_price: float
    booking_status: str
    created_at: datetime

    class Config:
        from_attributes = True