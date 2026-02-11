from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from bson import ObjectId

from app.core.database import get_database
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate, UserRole, UserUpdate
from app.core.security import verify_password, get_password_hash

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase


class UserCRUD:
    def __init__(self):
        self.collection_name = "users"

    async def create_user(self, user_data: UserCreate) -> dict:
        database = await get_database()
        assert database is not None
        user_dict = user_data.model_dump()
        password = user_dict.pop("password")
        # Truncate password to max 72 characters for bcrypt
        user_dict["hashed_password"] = get_password_hash(password[:72])
        user_dict["created_at"] = datetime.now()

        result = await database[self.collection_name].insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return user_dict

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        database = await get_database()
        assert database is not None
        user = await database[self.collection_name].find_one({"username": username})
        return user

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        database = await get_database()
        assert database is not None
        user = await database[self.collection_name].find_one({"email": email})
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        database = await get_database()
        assert database is not None
        user = await database[self.collection_name].find_one({"_id": ObjectId(user_id)})
        return user

    async def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        user = await self.get_user_by_username(username)
        if not user or not verify_password(password, user["hashed_password"]):
            return None
        return user

    async def update_user(
        self, user_id: str, user_update: UserUpdate
    ) -> Optional[dict]:
        database = await get_database()
        assert database is not None
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Handle password update separately
        current_password = update_data.pop("current_password", None)
        new_password = update_data.pop("new_password", None)
        
        if current_password and new_password:
            # Verify current password first
            user = await self.get_user_by_id(user_id)
            if not user or not verify_password(current_password, user["hashed_password"]):
                return None
            # Hash new password
            update_data["hashed_password"] = get_password_hash(new_password[:72])
        
        update_data["updated_at"] = datetime.now()

        result = await database[self.collection_name].update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )

        if result.modified_count:
            return await self.get_user_by_id(user_id)
        return None

    async def delete_user(self, user_id: str) -> bool:
        database = await get_database()
        assert database is not None
        result = await database[self.collection_name].delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[dict]:
        database = await get_database()
        assert database is not None
        users = (
            await database[self.collection_name]
            .find()
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
        return users

    async def create_admin_user(self):
        admin_exists = await self.get_user_by_username("admin")
        if not admin_exists:
            admin_user = UserCreate(
                username="admin",
                email="admin@newyears.com",
                password="admin123",
                role=UserRole.ADMIN,
            )
            await self.create_user(admin_user)
        organizer_exists = await self.get_user_by_username("organizer")
        if not organizer_exists:
            organizer_user = UserCreate(
                username="organizer",
                email="organizer@newyears.com",
                password="organizer123",
                role=UserRole.ORGANIZER,
            )
            await self.create_user(organizer_user)


user_crud = UserCRUD()
