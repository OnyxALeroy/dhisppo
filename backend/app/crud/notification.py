from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from bson import ObjectId

from app.core.database import get_database
from app.schemas.notification import NotificationCreate, NotificationUpdate

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase


class NotificationCRUD:
    def __init__(self):
        self.collection_name = "notifications"

    async def _get_user_info(self, user_id: str) -> dict:
        database = await get_database()
        try:
            user = await database["users"].find_one({"_id": ObjectId(user_id)})
            if user:
                return {
                    "id": str(user["_id"]),
                    "username": user.get("username", "Unknown"),
                    "email": user.get("email", "")
                }
        except Exception:
            pass
        return {"id": user_id, "username": "Unknown", "email": ""}

    async def create_notification(self, notification_data: NotificationCreate) -> dict:
        database = await get_database()
        assert database is not None
        notification_dict = notification_data.model_dump()
        notification_dict["read"] = False
        notification_dict["created_at"] = datetime.now()

        result = await database[self.collection_name].insert_one(notification_dict)
        notification_dict["_id"] = result.inserted_id
        return notification_dict

    async def get_notification_by_id(self, notification_id: str) -> Optional[dict]:
        database = await get_database()
        assert database is not None
        notification = await database[self.collection_name].find_one({"_id": ObjectId(notification_id)})
        return notification

    async def get_user_notifications(
        self, user_id: str, skip: int = 0, limit: int = 100, unread_only: bool = False
    ) -> List[dict]:
        database = await get_database()
        assert database is not None
        
        if unread_only:
            query = {"receiver_id": user_id, "read": False}
        else:
            query = {"receiver_id": user_id}
            
        notifications = (
            await database[self.collection_name]
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
        
        for notification in notifications:
            sender_info = await self._get_user_info(notification.get("sender_id", ""))
            notification["sender_username"] = sender_info["username"]
            
        return notifications

    async def mark_notification_as_read(self, notification_id: str) -> Optional[dict]:
        database = await get_database()
        assert database is not None
        
        result = await database[self.collection_name].update_one(
            {"_id": ObjectId(notification_id)}, 
            {"$set": {"read": True}}
        )

        if result.modified_count:
            return await self.get_notification_by_id(notification_id)
        return None

    async def mark_all_user_notifications_as_read(self, user_id: str) -> int:
        database = await get_database()
        assert database is not None
        
        result = await database[self.collection_name].update_many(
            {"receiver_id": user_id, "read": False},
            {"$set": {"read": True, "updated_at": datetime.now()}}
        )
        
        return result.modified_count

    async def delete_notification(self, notification_id: str) -> bool:
        database = await get_database()
        assert database is not None
        result = await database[self.collection_name].delete_one({"_id": ObjectId(notification_id)})
        return result.deleted_count > 0

    async def get_unread_notification_count(self, user_id: str) -> int:
        database = await get_database()
        assert database is not None
        query = {"receiver_id": user_id, "read": False}
        count = await database[self.collection_name].count_documents(query)
        return count


notification_crud = NotificationCRUD()