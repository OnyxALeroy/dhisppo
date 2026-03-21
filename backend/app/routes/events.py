from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.event import event_crud
from app.crud.notification import notification_crud
from app.crud.user import user_crud
from app.routes.auth import get_current_user_auth, get_organizer_or_admin_user
from app.schemas.event import EventCreate, EventResponse, EventUpdate, EventInvite, Participant
from app.schemas.notification import NotificationCreate
from app.schemas.payment import PaymentInDB
from app.schemas.user import UserRole

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse)
async def create_event(
    event: EventCreate, current_user: dict = Depends(get_organizer_or_admin_user)
):
    username = str(current_user["username"]) if current_user.get("username") else ""
    # Ensure organizers are all strings
    event.organizers = [str(org) for org in event.organizers if org]
    if username and username not in event.organizers:
        event.organizers.append(username)
    db_event = await event_crud.create_event(event)
    return EventResponse(
        id=str(db_event["_id"]),
        name=db_event["name"],
        organizers=db_event.get("organizers", []),
        locations=db_event.get("locations", []),
        description=db_event.get("description", ""),
        start_date=db_event["start_date"],
        end_date=db_event.get("end_date"),
        start_time=db_event["start_time"],
        end_time=db_event.get("end_time"),
        images=db_event.get("images", []),
        notes=db_event.get("notes", []),
        visibility=db_event.get("visibility", "public"),
        participants=[
            Participant(**participant)
            for participant in db_event.get("participants", [])
        ],
        payments=[],
        created_at=db_event["created_at"],
        updated_at=db_event.get("updated_at"),
    )


@router.get("/", response_model=list[EventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    organizer: Optional[str] = None,
    location: Optional[str] = None,
    q: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user_auth),
):
    user_id = str(current_user["_id"]) if current_user else None
    username = current_user["username"] if current_user else None
    role = current_user.get("role", "user") if current_user else "user"
    
    if q:
        events = await event_crud.search_events(q, user_id, username, role, skip, limit)
    elif organizer:
        events = await event_crud.get_events_by_organizer(organizer, user_id, username, role, skip, limit)
    elif location:
        events = await event_crud.get_events_by_location(location, user_id, username, role, skip, limit)
    elif current_user:
        events = await event_crud.get_events_for_user(user_id, username, role, skip, limit)
    else:
        events = await event_crud.get_events(skip, limit)

    return [
        EventResponse(
            id=str(event["_id"]),
            name=event.get("name", ""),
            organizers=event.get("organizers", []),
            locations=event.get("locations", []),
            description=event.get("description", ""),
            start_date=event["start_date"],
            end_date=event.get("end_date"),
            start_time=event["start_time"],
            end_time=event.get("end_time"),
            images=event.get("images", []),
            notes=event.get("notes", []),
            visibility=event.get("visibility", "public"),
            participants=[
                Participant(**participant)
                for participant in event.get("participants", [])
            ],
            payments=[
                PaymentInDB(**payment)
                for payment in event.get("payments", [])
            ],
            created_at=event["created_at"],
            updated_at=event.get("updated_at"),
        )
        for event in events
    ]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    current_user: Optional[dict] = Depends(get_current_user_auth)
):
    event = await event_crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    visibility = event.get("visibility", "public")
    if visibility == "private" and current_user:
        user_id = str(current_user["_id"])
        username = current_user["username"]
        role = current_user.get("role", "user")
        organizers = event.get("organizers", [])
        participants = [p.get("user_id") for p in event.get("participants", [])]
        
        if role != "admin" and username not in organizers and user_id not in participants:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this private event"
            )
    elif visibility == "private" and not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Login required to access private event"
        )

    # Build payments safely
    payments_data = event.get("payments", [])
    payments_list = []
    if payments_data:
        try:
            payments_list = [PaymentInDB(**payment) for payment in payments_data]
        except Exception as e:
            print(f"Error creating PaymentInDB: {e}")
            payments_list = []
    
    return EventResponse(
        id=str(event["_id"]),
        name=event.get("name", ""),
        organizers=event.get("organizers", []),
        locations=event.get("locations", []),
        description=event.get("description", ""),
        start_date=event["start_date"],
        end_date=event.get("end_date"),
        start_time=event["start_time"],
        end_time=event.get("end_time"),
        images=event.get("images", []),
        notes=event.get("notes", []),
        visibility=visibility,
        participants=[
            Participant(**participant) for participant in event.get("participants", [])
        ],
        payments=payments_list,
        created_at=event["created_at"],
        updated_at=event.get("updated_at"),
    )


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    current_user: dict = Depends(get_current_user_auth),
):
    event = await event_crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    user_role = current_user.get("role")
    username = current_user["username"]

    if not (
        user_role == UserRole.ADMIN
        or (user_role == UserRole.ORGANIZER and username in event.get("organizers", []))
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this event.",
        )

    updated_event = await event_crud.update_event(event_id, event_update)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    return EventResponse(
        id=str(updated_event["_id"]),
        name=updated_event.get("name", ""),
        organizers=updated_event.get("organizers", []),
        locations=updated_event.get("locations", []),
        description=updated_event.get("description", ""),
        start_date=updated_event["start_date"],
        end_date=updated_event.get("end_date"),
        start_time=updated_event["start_time"],
        end_time=updated_event.get("end_time"),
        images=updated_event.get("images", []),
        notes=updated_event.get("notes", []),
        visibility=updated_event.get("visibility", "public"),
        participants=[
            Participant(**p)
            for p in updated_event.get("participants", [])
        ],
        payments=[
            PaymentInDB(**payment)
            for payment in updated_event.get("payments", [])
        ],
        created_at=updated_event["created_at"],
        updated_at=updated_event.get("updated_at"),
    )


@router.post("/{event_id}/invite", status_code=status.HTTP_201_CREATED)
async def invite_user_to_event(
    event_id: str,
    invite: EventInvite,
    current_user: dict = Depends(get_current_user_auth)
):
    event = await event_crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    user_role = current_user.get("role", "user")
    username = current_user["username"]
    organizers = event.get("organizers", [])

    if user_role != "admin" and username not in organizers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or organizers can send invitations",
        )

    target_user = await user_crud.get_user_by_id(invite.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_participants = [p.get("user_id") for p in event.get("participants", [])]
    if invite.user_id in existing_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a participant",
        )

    notification = NotificationCreate(
        sender_id=str(current_user["_id"]),
        receiver_id=invite.user_id,
        content=f"invite:{event_id}:{event.get('name', 'unknown')}",
    )
    await notification_crud.create_notification(notification)

    return {"message": f"Invitation sent to user {target_user.get('username', invite.user_id)}"}


@router.post("/invitations/{event_id}/accept", response_model=EventResponse)
async def accept_event_invitation(
    event_id: str,
    current_user: dict = Depends(get_current_user_auth)
):
    event = await event_crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    user_id = str(current_user["_id"])
    existing_participants = [p.get("user_id") for p in event.get("participants", [])]
    
    if user_id in existing_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a participant",
        )

    participant = Participant(
        user_id=user_id,
        tags=[],
        due_payment=0,
        paid_amount=0
    )

    updated_event = await event_crud.add_participant(event_id, participant)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return EventResponse(
        id=str(updated_event["_id"]),
        name=updated_event.get("name", ""),
        organizers=updated_event.get("organizers", []),
        locations=updated_event.get("locations", []),
        description=updated_event.get("description", ""),
        start_date=updated_event["start_date"],
        end_date=updated_event.get("end_date"),
        start_time=updated_event["start_time"],
        end_time=updated_event.get("end_time"),
        images=updated_event.get("images", []),
        notes=updated_event.get("notes", []),
        visibility=updated_event.get("visibility", "public"),
        participants=[
            Participant(**p)
            for p in updated_event.get("participants", [])
        ],
        payments=[
            PaymentInDB(**payment)
            for payment in updated_event.get("payments", [])
        ],
        created_at=updated_event["created_at"],
        updated_at=updated_event.get("updated_at"),
    )

@router.post("/{event_id}/participants", response_model=EventResponse)
async def add_participant(
    event_id: str,
    participant: Participant,
    current_user: dict = Depends(get_current_user_auth)
):
    event = await event_crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    user_id = str(current_user["_id"])
    username = current_user["username"]
    role = current_user.get("role", "user")
    organizers = event.get("organizers", [])
    visibility = event.get("visibility", "public")

    if visibility == "private":
        if role != "admin" and username not in organizers:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot join private event without invitation from organizer",
            )

    existing_participants = [p.get("user_id") for p in event.get("participants", [])]
    if participant.user_id in existing_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a participant",
        )

    updated_event = await event_crud.add_participant(event_id, participant)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return EventResponse(
        id=str(updated_event["_id"]),
        name=updated_event.get("name", ""),
        organizers=updated_event.get("organizers", []),
        locations=updated_event.get("locations", []),
        description=updated_event.get("description", ""),
        start_date=updated_event["start_date"],
        end_date=updated_event.get("end_date"),
        start_time=updated_event["start_time"],
        end_time=updated_event.get("end_time"),
        images=updated_event.get("images", []),
        notes=updated_event.get("notes", []),
        visibility=updated_event.get("visibility", "public"),
        participants=[
            Participant(**p)
            for p in updated_event.get("participants", [])
        ],
        payments=[
            PaymentInDB(**payment)
            for payment in updated_event.get("payments", [])
        ],
        created_at=updated_event["created_at"],
        updated_at=updated_event.get("updated_at"),
    )

@router.delete("/{event_id}/participants/{user_id}", response_model=EventResponse)
async def delete_participant(
    event_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_user_auth)
):
    event = await event_crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    username = current_user["username"]
    role = current_user.get("role", "user")
    organizers = event.get("organizers", [])
    
    # Allow admins, organizers of the event, or the user removing themselves
    if role != "admin" and username not in organizers and username != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only remove yourself or be removed by an organizer/admin",
        )
    
    updated_event = await event_crud.remove_participant(event_id, user_id)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or participant not in event",
        )

    return EventResponse(
        id=str(updated_event["_id"]),
        name=updated_event.get("name", ""),
        organizers=updated_event.get("organizers", []),
        locations=updated_event.get("locations", []),
        description=updated_event.get("description", ""),
        start_date=updated_event["start_date"],
        end_date=updated_event.get("end_date"),
        start_time=updated_event["start_time"],
        end_time=updated_event.get("end_time"),
        images=updated_event.get("images", []),
        notes=updated_event.get("notes", []),
        visibility=updated_event.get("visibility", "public"),
        participants=[
            Participant(**p)
            for p in updated_event.get("participants", [])
        ],
        payments=[
            PaymentInDB(**payment)
            for payment in updated_event.get("payments", [])
        ],
        created_at=updated_event["created_at"],
        updated_at=updated_event.get("updated_at"),
    )


@router.patch(
    "/{event_id}/participants/{user_id}/payment", response_model=EventResponse
)
async def update_participant_payment(
    event_id: str,
    user_id: str,
    paid_amount: float,
    current_user: dict = Depends(get_current_user_auth),
):
    if paid_amount < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paid amount cannot be negative",
        )

    updated_event = await event_crud.update_participant_payment(
        event_id, user_id, paid_amount
    )
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or participant not in event",
        )

    return EventResponse(
        id=str(updated_event["_id"]),
        name=updated_event.get("name", ""),
        organizers=updated_event.get("organizers", []),
        locations=updated_event.get("locations", []),
        description=updated_event.get("description", ""),
        start_date=updated_event["start_date"],
        end_date=updated_event.get("end_date"),
        start_time=updated_event["start_time"],
        end_time=updated_event.get("end_time"),
        images=updated_event.get("images", []),
        notes=updated_event.get("notes", []),
        visibility=updated_event.get("visibility", "public"),
        participants=[
            Participant(**participant)
            for participant in updated_event.get("participants", [])
        ],
        created_at=updated_event["created_at"],
        updated_at=updated_event.get("updated_at"),
    )