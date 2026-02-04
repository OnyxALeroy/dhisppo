from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    id: str = Field(description="User ID")
    username: str = Field(description="Username for display")
    email: Optional[str] = Field(None, description="User email for display")


class PaymentBase(BaseModel):
    sender: UserInfo = Field(description="Payment sender information")
    receiver: UserInfo = Field(description="Payment receiver information")
    amount: float = Field(description="Payment amount", gt=0)
    title: str = Field(description="Payment title/description")


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    title: Optional[str] = None


class PaymentInDB(PaymentBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class PaymentResponse(PaymentBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True