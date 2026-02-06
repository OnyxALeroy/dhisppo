from datetime import datetime
from typing import List, Optional
import uuid
from bson import ObjectId

from app.core.database import get_database
from app.crud.user import user_crud
from app.schemas.expenditure import ExpenditureCreate, ExpenditureUpdate
from app.schemas.payment import UserInfo


class ExpenditureCRUD:
    def __init__(self, collection_name: str = "events"):
        self.collection_name = collection_name

    async def get_user_info(self, user_id: str) -> Optional[dict]:
        """Get user information for display"""
        user = await user_crud.get_user_by_id(user_id)
        if user:
            return {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user.get("email"),
            }
        return {"id": user_id, "username": "Unknown", "email": None}

    async def create_expenditure(self, event_id: str, expenditure_data: ExpenditureCreate):
        """Create a new expenditure for an event"""
        # Get user info for the payer
        payer_info = await self.get_user_info(expenditure_data.payer_id)
        if not payer_info or payer_info["username"] == "Unknown":
            raise ValueError(f"User with ID {expenditure_data.payer_id} not found")

        # Convert to UserInfo object
        payer_user_info = UserInfo(**payer_info)

        expenditure_dict = {
            "id": str(uuid.uuid4()),
            "payer_id": expenditure_data.payer_id,
            "payer": payer_user_info.dict(),
            "amount": expenditure_data.amount,
            "receiver": expenditure_data.receiver,
            "description": expenditure_data.description,
            "type": expenditure_data.type.value if hasattr(expenditure_data.type, 'value') else expenditure_data.type,
            "created_at": datetime.utcnow(),
        }

        db = await get_database()
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(event_id)},
            {
                "$push": {"expenditures": expenditure_dict},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )

        if result.matched_count == 0:
            return None

        return expenditure_dict

    async def get_expenditures_by_event(self, event_id: str) -> List[dict]:
        """Get all expenditures for an event"""
        db = await get_database()
        event = await db[self.collection_name].find_one({"_id": ObjectId(event_id)})
        if not event:
            return []
        
        expenditures = event.get("expenditures", [])
        # Handle legacy data - ensure all expenditures have required fields
        normalized_expenditures = []
        for expenditure in expenditures:
            # If expenditure has payer_id but no payer info, fetch it
            if "payer_id" in expenditure and "payer" not in expenditure:
                payer_info = await self.get_user_info(expenditure["payer_id"])
                expenditure["payer"] = payer_info
            # If expenditure has payer but no payer_id, extract it from payer.id
            elif "payer" in expenditure and "payer_id" not in expenditure:
                expenditure["payer_id"] = expenditure["payer"].get("id", "")
            # If neither exists, use empty values
            elif "payer_id" not in expenditure and "payer" not in expenditure:
                expenditure["payer_id"] = ""
                expenditure["payer"] = {"id": "", "username": "Unknown", "email": None}
            
            # Ensure type field exists for legacy data
            if "type" not in expenditure:
                expenditure["type"] = "other"
            
            normalized_expenditures.append(expenditure)
        
        return normalized_expenditures

    async def get_expenditure(self, event_id: str, expenditure_id: str) -> Optional[dict]:
        """Get a specific expenditure by ID"""
        db = await get_database()
        event = await db[self.collection_name].find_one({"_id": ObjectId(event_id)})
        if not event:
            return None

        expenditures = event.get("expenditures", [])
        for expenditure in expenditures:
            if expenditure["id"] == expenditure_id:
                # Handle legacy data - ensure all expenditures have required fields
                if "payer_id" in expenditure and "payer" not in expenditure:
                    payer_info = await self.get_user_info(expenditure["payer_id"])
                    expenditure["payer"] = payer_info
                elif "payer" in expenditure and "payer_id" not in expenditure:
                    expenditure["payer_id"] = expenditure["payer"].get("id", "")
                elif "payer_id" not in expenditure and "payer" not in expenditure:
                    expenditure["payer_id"] = ""
                    expenditure["payer"] = {"id": "", "username": "Unknown", "email": None}
                
                # Ensure type field exists for legacy data
                if "type" not in expenditure:
                    expenditure["type"] = "other"
                
                return expenditure
        return None

    async def update_expenditure(
        self, event_id: str, expenditure_id: str, expenditure_update: ExpenditureUpdate
    ):
        """Update an existing expenditure"""
        # Build update document with only provided fields
        update_doc = {"$set": {}}
        
        if expenditure_update.amount is not None:
            update_doc["$set"]["expenditures.$.amount"] = expenditure_update.amount
        if expenditure_update.receiver is not None:
            update_doc["$set"]["expenditures.$.receiver"] = expenditure_update.receiver
        if expenditure_update.description is not None:
            update_doc["$set"]["expenditures.$.description"] = expenditure_update.description
        if expenditure_update.type is not None:
            update_doc["$set"]["expenditures.$.type"] = expenditure_update.type.value if hasattr(expenditure_update.type, 'value') else expenditure_update.type
        
        # Always update the modified timestamp
        update_doc["$set"]["updated_at"] = datetime.utcnow()

        db = await get_database()
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(event_id), "expenditures.id": expenditure_id},
            update_doc,
        )

        if result.matched_count == 0:
            return None

        return await self.get_expenditure(event_id, expenditure_id)

    async def delete_expenditure(self, event_id: str, expenditure_id: str):
        """Delete an expenditure"""
        db = await get_database()
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(event_id)},
            {
                "$pull": {"expenditures": {"id": expenditure_id}},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )

        if result.matched_count == 0:
            return None

        return True

    async def get_expenditures_by_user(
        self, user_id: str, as_payer: bool = True
    ) -> List[dict]:
        """Get all expenditures for a user (as payer)"""
        match_stage = {}
        
        if as_payer:
            match_stage = {"expenditures.payer.id": user_id}

        db = await get_database()
        events = await db[self.collection_name].aggregate([
            {"$match": {"expenditures": {"$exists": True, "$ne": []}}},
            {"$unwind": "$expenditures"},
            {"$match": match_stage},
            {
                "$project": {
                    "event_id": {"$toString": "$_id"},
                    "event_name": "$name",
                    "expenditure": "$expenditures"
                }
            }
        ]).to_list(length=None)
        
        return events


expenditure_crud = ExpenditureCRUD()