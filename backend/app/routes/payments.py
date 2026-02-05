from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.payment import payment_crud
from app.crud.event import event_crud
from app.routes.auth import get_current_user_auth, get_organizer_or_admin_user
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate, UserInfo
from app.schemas.event import EventResponse, Participant
from app.schemas.user import UserRole

router = APIRouter(prefix="/payments", tags=["payments"])


def generate_payment_id():
    """Generate a unique payment ID"""
    return str(uuid.uuid4())


async def verify_user_exists(user_id: str) -> UserInfo:
    """Verify user exists and return user info"""
    user_info = await payment_crud.get_user_info(user_id)
    if not user_info or user_info["username"] == "Unknown":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return UserInfo(**user_info)


async def check_event_permission(event_id: str, current_user: dict) -> dict:
    """Check if current user has permission to access event"""
    event = await event_crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    user_role = current_user.get("role")
    user_id = str(current_user["_id"])

    # Check if user is admin or event organizer
    if not (
        user_role == UserRole.ADMIN
        or (user_role == UserRole.ORGANIZER and user_id in event.get("organizers", []))
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage payments for this event"
        )
    
    return event


@router.post("/events/{event_id}/payments")
async def create_payment(
    event_id: str,
    payment: PaymentCreate,
    current_user: dict = Depends(get_organizer_or_admin_user)
):
    """Create a new payment for an event"""
    
    # Verify event exists and user has permission
    await check_event_permission(event_id, current_user)
    
    # Verify sender and receiver users exist
    await verify_user_exists(payment.sender.id)
    await verify_user_exists(payment.receiver.id)
    
    # Add ID to payment data
    payment_dict = payment.dict()
    payment_dict["id"] = generate_payment_id()
    payment_create = PaymentCreate(**payment_dict)
    
    updated_event = await payment_crud.create_payment(event_id, payment_create)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return {"message": "Payment created successfully", "event_id": event_id}


@router.get("/events/{event_id}/payments", response_model=List[PaymentResponse])
async def get_event_payments(
    event_id: str,
    current_user: dict = Depends(get_current_user_auth)
):
    """Get all payments for an event"""
    
    # Verify event exists and user has permission
    await check_event_permission(event_id, current_user)
    
    payments = await payment_crud.get_payments_by_event(event_id)
    
    return [
        PaymentResponse(
            id=payment["id"],
            sender=UserInfo(**payment["sender"]),
            receiver=UserInfo(**payment["receiver"]),
            amount=payment["amount"],
            title=payment["title"],
            created_at=payment["created_at"]
        )
        for payment in payments
    ]


@router.get("/events/{event_id}/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    event_id: str,
    payment_id: str,
    current_user: dict = Depends(get_current_user_auth)
):
    """Get a specific payment"""
    
    # Verify event exists and user has permission
    await check_event_permission(event_id, current_user)
    
    payment = await payment_crud.get_payment(event_id, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentResponse(
        id=payment["id"],
        sender=UserInfo(**payment["sender"]),
        receiver=UserInfo(**payment["receiver"]),
        amount=payment["amount"],
        title=payment["title"],
        created_at=payment["created_at"]
    )


@router.patch("/events/{event_id}/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    event_id: str,
    payment_id: str,
    payment_update: PaymentUpdate,
    current_user: dict = Depends(get_current_user_auth)
):
    """Update a payment"""
    
    # Verify event exists and user has permission
    await check_event_permission(event_id, current_user)
    
    # Check if payment exists
    existing_payment = await payment_crud.get_payment(event_id, payment_id)
    if not existing_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    updated_event = await payment_crud.update_payment(event_id, payment_id, payment_update)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Get the updated payment
    updated_payment = await payment_crud.get_payment(event_id, payment_id)
    if not updated_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentResponse(
        id=updated_payment["id"],
        sender=UserInfo(**updated_payment["sender"]),
        receiver=UserInfo(**updated_payment["receiver"]),
        amount=updated_payment["amount"],
        title=updated_payment["title"],
        created_at=updated_payment["created_at"]
    )


@router.delete("/events/{event_id}/payments/{payment_id}")
async def delete_payment(
    event_id: str,
    payment_id: str,
    current_user: dict = Depends(get_organizer_or_admin_user)
):
    """Delete a payment"""
    
    # Verify event exists and user has permission
    await check_event_permission(event_id, current_user)
    
    # Check if payment exists
    existing_payment = await payment_crud.get_payment(event_id, payment_id)
    if not existing_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    updated_event = await payment_crud.delete_payment(event_id, payment_id)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return {"message": "Payment deleted successfully", "event_id": event_id}


@router.get("/user/{user_id}/payments")
async def get_user_payments(
    user_id: str,
    as_sender: bool = True,
    as_receiver: bool = True,
    current_user: dict = Depends(get_current_user_auth)
):
    """Get all payments for a user (as sender and/or receiver)"""
    
    # Check if user is requesting their own payments or is admin
    current_user_id = str(current_user["_id"])
    if current_user_id != user_id and current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own payments"
        )
    
    payments_with_events = await payment_crud.get_payments_by_user(user_id, as_sender, as_receiver)
    
    return [
        {
            "event_id": result["event_id"],
            "event_name": result["event_name"],
            "payment": PaymentResponse(
                id=result["payment"]["id"],
                sender=UserInfo(**result["payment"]["sender"]),
                receiver=UserInfo(**result["payment"]["receiver"]),
                amount=result["payment"]["amount"],
                title=result["payment"]["title"],
                created_at=result["payment"]["created_at"]
            )
        }
        for result in payments_with_events
    ]


@router.get("/my/payments")
async def get_my_payments(
    as_sender: bool = True,
    as_receiver: bool = True,
    current_user: dict = Depends(get_current_user_auth)
):
    """Get all payments for current user"""
    
    user_id = str(current_user["_id"])
    payments_with_events = await payment_crud.get_payments_by_user(user_id, as_sender, as_receiver)
    
    return [
        {
            "event_id": result["event_id"],
            "event_name": result["event_name"],
            "payment": PaymentResponse(
                id=result["payment"]["id"],
                sender=UserInfo(**result["payment"]["sender"]),
                receiver=UserInfo(**result["payment"]["receiver"]),
                amount=result["payment"]["amount"],
                title=result["payment"]["title"],
                created_at=result["payment"]["created_at"]
            )
        }
        for result in payments_with_events
    ]


@router.get("/my/payment-summary")
async def get_my_payment_summary(
    current_user: dict = Depends(get_current_user_auth)
):
    """Get payment summary for current user (total given and total received)"""
    
    user_id = str(current_user["_id"])
    payments_with_events = await payment_crud.get_payments_by_user(user_id, as_sender=True, as_receiver=True)
    
    total_given = 0.0
    total_received = 0.0
    
    for result in payments_with_events:
        payment = result["payment"]
        if payment["sender"]["id"] == user_id:
            total_given += payment["amount"]
        if payment["receiver"]["id"] == user_id:
            total_received += payment["amount"]
    
    return {
        "total_given": total_given,
        "total_received": total_received
    }