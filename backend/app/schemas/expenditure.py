from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from .payment import UserInfo
from enum import Enum


class ExpenditureType(str, Enum):
    LOCATION = "location"
    FOOD = "food"
    OTHER = "other"


class ExpenditureBase(BaseModel):
    payer_id: str = Field(description="User ID of the person who paid")
    payer: UserInfo = Field(description="Payer user information for display")
    amount: float = Field(description="Expenditure amount", gt=0)
    receiver: str = Field(description="Who/what received the payment (vendor, service, etc.)")
    description: str = Field(description="Description of the expenditure")
    type: ExpenditureType = Field(default=ExpenditureType.OTHER, description="Type of expenditure")


class ExpenditureCreate(BaseModel):
    payer_id: str = Field(description="User ID of the person who paid")
    amount: float = Field(description="Expenditure amount", gt=0)
    receiver: str = Field(description="Who/what received the payment (vendor, service, etc.)")
    description: str = Field(description="Description of the expenditure")
    type: ExpenditureType = Field(default=ExpenditureType.OTHER, description="Type of expenditure")


class ExpenditureUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    receiver: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ExpenditureType] = None


class ExpenditureInDB(ExpenditureBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ExpenditureResponse(BaseModel):
    id: str
    payer_id: str
    payer: UserInfo
    amount: float
    receiver: str
    description: str
    type: ExpenditureType
    created_at: datetime

    class Config:
        from_attributes = True