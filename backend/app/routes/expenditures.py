from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.expenditure import expenditure_crud
from app.crud.event import event_crud
from app.routes.auth import get_current_user_auth, get_organizer_or_admin_user
from app.schemas.expenditure import ExpenditureCreate, ExpenditureResponse, ExpenditureUpdate, ExpenditureType
from app.schemas.user import UserRole

router = APIRouter(prefix="/expenditures", tags=["expenditures"])


def generate_expenditure_id():
    """Generate a unique expenditure ID"""
    return str(uuid.uuid4())


async def verify_user_exists(user_id: str) -> bool:
    """Verify user exists"""
    user_info = await expenditure_crud.get_user_info(user_id)
    if not user_info or user_info["username"] == "Unknown":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return True


async def check_event_permission(event_id: str, current_user: dict) -> dict:
    """Check if current user has permission to access event"""
    event = await event_crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    user_role = current_user.get("role")
    username = current_user.get("username")

    # Check if user is admin or event organizer (organizers are stored by username)
    if not (
        user_role == UserRole.ADMIN
        or (user_role == UserRole.ORGANIZER and username in event.get("organizers", []))
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage expenditures for this event"
        )
    
    return event


@router.post("/events/{event_id}/expenditures")
async def create_expenditure(
    event_id: str,
    expenditure: ExpenditureCreate,
    current_user: dict = Depends(get_organizer_or_admin_user)
):
    """Create a new expenditure for an event"""
    
    # Verify event exists and user has permission
    await check_event_permission(event_id, current_user)
    
    # Verify payer user exists
    await verify_user_exists(expenditure.payer_id)
    
    # Add ID to expenditure data
    expenditure_dict = expenditure.dict()
    expenditure_dict["id"] = generate_expenditure_id()
    expenditure_create = ExpenditureCreate(**expenditure_dict)
    
    updated_event = await expenditure_crud.create_expenditure(event_id, expenditure_create)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return {"message": "Expenditure created successfully", "event_id": event_id}


@router.get("/events/{event_id}/expenditures", response_model=List[ExpenditureResponse])
async def get_event_expenditures(
    event_id: str,
    current_user: dict = Depends(get_current_user_auth)
):
    """Get all expenditures for an event"""
    
    # Verify event exists and user has permission
    event = await check_event_permission(event_id, current_user)
    
    expenditures = await expenditure_crud.get_expenditures_by_event(event_id)
    
    return [
        ExpenditureResponse(
            id=expenditure["id"],
            payer_id=expenditure["payer_id"],
            payer=expenditure["payer"],
            amount=expenditure["amount"],
            receiver=expenditure["receiver"],
            description=expenditure["description"],
            type=expenditure["type"],
            created_at=expenditure["created_at"]
        )
        for expenditure in expenditures
    ]


@router.get("/events/{event_id}/expenditures/{expenditure_id}", response_model=ExpenditureResponse)
async def get_expenditure(
    event_id: str,
    expenditure_id: str,
    current_user: dict = Depends(get_current_user_auth)
):
    """Get a specific expenditure"""
    
    # Verify event exists and user has permission
    await check_event_permission(event_id, current_user)
    
    expenditure = await expenditure_crud.get_expenditure(event_id, expenditure_id)
    if not expenditure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expenditure not found"
        )
    
    return ExpenditureResponse(
        id=expenditure["id"],
        payer_id=expenditure["payer_id"],
        payer=expenditure["payer"],
        amount=expenditure["amount"],
        receiver=expenditure["receiver"],
        description=expenditure["description"],
        type=ExpenditureType(expenditure["type"]),
        created_at=expenditure["created_at"]
    )


@router.patch("/events/{event_id}/expenditures/{expenditure_id}", response_model=ExpenditureResponse)
async def update_expenditure(
    event_id: str,
    expenditure_id: str,
    expenditure_update: ExpenditureUpdate,
    current_user: dict = Depends(get_organizer_or_admin_user)
):
    """Update an expenditure"""
    
    # Verify event exists and user has permission
    await check_event_permission(event_id, current_user)
    
    # Check if expenditure exists
    existing_expenditure = await expenditure_crud.get_expenditure(event_id, expenditure_id)
    if not existing_expenditure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expenditure not found"
        )
    
    updated_expenditure = await expenditure_crud.update_expenditure(event_id, expenditure_id, expenditure_update)
    if not updated_expenditure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expenditure not found"
        )
    
    return ExpenditureResponse(
        id=updated_expenditure["id"],
        payer_id=updated_expenditure["payer_id"],
        payer=updated_expenditure["payer"],
        amount=updated_expenditure["amount"],
        receiver=updated_expenditure["receiver"],
        description=updated_expenditure["description"],
        type=ExpenditureType(updated_expenditure["type"]),
        created_at=updated_expenditure["created_at"]
    )


@router.delete("/events/{event_id}/expenditures/{expenditure_id}")
async def delete_expenditure(
    event_id: str,
    expenditure_id: str,
    current_user: dict = Depends(get_organizer_or_admin_user)
):
    """Delete an expenditure"""
    
    # Verify event exists and user has permission
    await check_event_permission(event_id, current_user)
    
    # Check if expenditure exists
    existing_expenditure = await expenditure_crud.get_expenditure(event_id, expenditure_id)
    if not existing_expenditure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expenditure not found"
        )
    
    deleted = await expenditure_crud.delete_expenditure(event_id, expenditure_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expenditure not found"
        )

    return {"message": "Expenditure deleted successfully", "event_id": event_id}


@router.get("/user/{user_id}/expenditures")
async def get_user_expenditures(
    user_id: str,
    current_user: dict = Depends(get_current_user_auth)
):
    """Get all expenditures for a user (as payer)"""
    
    # Check if user is requesting their own expenditures or is admin
    current_user_id = str(current_user["_id"])
    if current_user_id != user_id and current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own expenditures"
        )
    
    expenditures_with_events = await expenditure_crud.get_expenditures_by_user(user_id, as_payer=True)
    
    return [
        {
            "event_id": result["event_id"],
            "event_name": result["event_name"],
            "expenditure": ExpenditureResponse(
                id=result["expenditure"]["id"],
                payer_id=result["expenditure"]["payer_id"],
                payer=result["expenditure"]["payer"],
                amount=result["expenditure"]["amount"],
                receiver=result["expenditure"]["receiver"],
                description=result["expenditure"]["description"],
                type=ExpenditureType(result["expenditure"]["type"]),
                created_at=result["expenditure"]["created_at"]
            )
        }
        for result in expenditures_with_events
    ]


@router.get("/my/expenditures")
async def get_my_expenditures(
    current_user: dict = Depends(get_current_user_auth)
):
    """Get all expenditures for current user"""
    
    user_id = str(current_user["_id"])
    expenditures_with_events = await expenditure_crud.get_expenditures_by_user(user_id, as_payer=True)
    
    return [
        {
            "event_id": result["event_id"],
            "event_name": result["event_name"],
            "expenditure": ExpenditureResponse(
                id=result["expenditure"]["id"],
                payer_id=result["expenditure"]["payer_id"],
                payer=result["expenditure"]["payer"],
                amount=result["expenditure"]["amount"],
                receiver=result["expenditure"]["receiver"],
                description=result["expenditure"]["description"],
                type=ExpenditureType(result["expenditure"]["type"]),
                created_at=result["expenditure"]["created_at"]
            )
        }
        for result in expenditures_with_events
    ]


@router.get("/my/expenditure-summary")
async def get_my_expenditure_summary(
    current_user: dict = Depends(get_current_user_auth)
):
    """Get expenditure summary for current user (total amount spent)"""
    
    user_id = str(current_user["_id"])
    expenditures_with_events = await expenditure_crud.get_expenditures_by_user(user_id, as_payer=True)
    
    total_spent = 0.0
    
    for result in expenditures_with_events:
        expenditure = result["expenditure"]
        total_spent += expenditure["amount"]
    
    return {
        "total_spent": total_spent
    }