from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationBase(BaseModel):
    sender_id: str
    receiver_id: str
    content: str


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    read: Optional[bool] = None


class NotificationInDB(NotificationBase):
    id: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    content: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True