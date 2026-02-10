from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.crud.notification import notification_crud
from app.routes.auth import get_current_user_auth
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    current_user: dict = Depends(get_current_user_auth)
):
    # Verify sender is the current user
    if notification.sender_id != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only send notifications as yourself"
        )
    
    db_notification = await notification_crud.create_notification(notification)
    return NotificationResponse(
        id=str(db_notification["_id"]),
        sender_id=db_notification["sender_id"],
        receiver_id=db_notification["receiver_id"],
        content=db_notification["content"],
        read=db_notification["read"],
        created_at=db_notification["created_at"],
    )


@router.get("/", response_model=List[NotificationResponse])
async def get_user_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    unread_only: bool = Query(False),
    current_user: dict = Depends(get_current_user_auth)
):
    user_id = str(current_user["_id"])
    notifications = await notification_crud.get_user_notifications(
        user_id=user_id, skip=skip, limit=limit, unread_only=unread_only
    )
    
    return [
        NotificationResponse(
            id=str(notification["_id"]),
            sender_id=notification["sender_id"],
            receiver_id=notification["receiver_id"],
            content=notification["content"],
            read=notification["read"],
            created_at=notification["created_at"],
        )
        for notification in notifications
    ]


@router.get("/unread-count")
async def get_unread_notification_count(
    current_user: dict = Depends(get_current_user_auth)
):
    user_id = str(current_user["_id"])
    count = await notification_crud.get_unread_notification_count(user_id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user_auth)
):
    # First get the notification to verify ownership
    notification = await notification_crud.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Verify the receiver is the current user
    if notification["receiver_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only mark your own notifications as read"
        )
    
    updated_notification = await notification_crud.mark_notification_as_read(notification_id)
    if not updated_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return NotificationResponse(
        id=str(updated_notification["_id"]),
        sender_id=updated_notification["sender_id"],
        receiver_id=updated_notification["receiver_id"],
        content=updated_notification["content"],
        read=updated_notification["read"],
        created_at=updated_notification["created_at"],
    )


@router.patch("/read-all")
async def mark_all_notifications_as_read(
    current_user: dict = Depends(get_current_user_auth)
):
    user_id = str(current_user["_id"])
    modified_count = await notification_crud.mark_all_user_notifications_as_read(user_id)
    return {"message": f"Marked {modified_count} notifications as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user_auth)
):
    # First get the notification to verify ownership
    notification = await notification_crud.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Verify the receiver is the current user
    if notification["receiver_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own notifications"
        )
    
    success = await notification_crud.delete_notification(notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification deleted successfully"}