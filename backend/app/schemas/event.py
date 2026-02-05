from datetime import datetime, date, time
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from .payment import PaymentInDB
from .expenditure import ExpenditureInDB


class Participant(BaseModel):
    user_id: str
    tags: List[str] = Field(
        default_factory=list, description="e.g., ['vegan', 'halal']"
    )
    due_payment: float = Field(default=0.0, ge=0)
    paid_amount: float = Field(default=0.0, ge=0)


class EventBase(BaseModel):
    name: str = Field(description="Event name")
    organizers: List[str] = Field(description="At least one organizer required")
    locations: List[str] = Field(description="At least one location required")
    description: str
    start_date: date = Field(description="Event start date")
    end_date: Optional[date] = Field(None, description="Event end date (optional for single day events)")
    start_time: time = Field(description="Event start time (mandatory)")
    end_time: Optional[time] = Field(None, description="Event end time (optional)")
    images: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class EventCreate(EventBase):
    participants: List[Participant] = Field(default_factory=list)
    payments: List[PaymentInDB] = Field(default_factory=list)
    expenditures: List[ExpenditureInDB] = Field(default_factory=list)


class EventUpdate(BaseModel):
    name: Optional[str] = None
    organizers: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    images: Optional[List[str]] = None
    notes: Optional[List[str]] = None
    participants: Optional[List[Participant]] = None
    payments: Optional[List[PaymentInDB]] = None
    expenditures: Optional[List[ExpenditureInDB]] = None


class EventInDB(EventBase):
    id: str
    participants: List[Participant]
    payments: List[PaymentInDB] = Field(default_factory=list)
    expenditures: List[ExpenditureInDB] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    id: str
    name: str
    organizers: List[str]
    locations: List[str]
    description: str
    start_date: date
    end_date: Optional[date] = None
    start_time: time
    end_time: Optional[time] = None
    images: List[str]
    notes: List[str]
    participants: List[Participant]
    payments: List[PaymentInDB] = Field(default_factory=list)
    expenditures: List[ExpenditureInDB] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
