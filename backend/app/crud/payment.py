from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from app.core.database import get_database
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentCRUD:
    def __init__(self):
        self.collection_name = "events"

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from the users collection"""
        database = await get_database()
        try:
            user = await database["users"].find_one({"_id": ObjectId(user_id)})
            if user:
                return {
                    "id": str(user["_id"]),
                    "username": user.get("username", ""),
                    "email": user.get("email", "")
                }
        except Exception:
            pass
        return {"id": user_id, "username": "Unknown", "email": ""}

    async def create_payment(self, event_id: str, payment_data: PaymentCreate) -> Optional[dict]:
        database = await get_database()
        
        # Get detailed user information for sender and receiver
        sender_info = await self.get_user_info(payment_data.sender.id)
        receiver_info = await self.get_user_info(payment_data.receiver.id)
        
        # Create payment document with detailed user info and ID
        payment_dict = {
            "id": str(uuid.uuid4()),
            "sender": sender_info,
            "receiver": receiver_info,
            "amount": payment_data.amount,
            "title": payment_data.title,
            "created_at": datetime.utcnow()
        }
        
        result = await database[self.collection_name].update_one(
            {"_id": ObjectId(event_id)},
            {
                "$push": {"payments": payment_dict},
                "$set": {"updated_at": datetime.utcnow()},
            }
        )
        
        if result.modified_count:
            return await self.get_event_by_id(event_id)
        return None

    async def get_event_by_id(self, event_id: str) -> Optional[dict]:
        database = await get_database()
        event = await database[self.collection_name].find_one(
            {"_id": ObjectId(event_id)}
        )
        return event

    async def get_payment(self, event_id: str, payment_id: str) -> Optional[dict]:
        database = await get_database()
        event = await database[self.collection_name].find_one(
            {"_id": ObjectId(event_id), "payments.id": payment_id}
        )
        
        if not event:
            return None
            
        # Find the specific payment in the payments array
        for payment in event.get("payments", []):
            if payment.get("id") == payment_id:
                return payment
        
        return None

    async def get_payments_by_event(self, event_id: str) -> List[dict]:
        database = await get_database()
        event = await database[self.collection_name].find_one(
            {"_id": ObjectId(event_id)}
        )
        
        if not event:
            return []
            
        return event.get("payments", [])

    async def get_payments_by_user(self, user_id: str, as_sender: bool = True, as_receiver: bool = True) -> List[dict]:
        database = await get_database()
        
        if not as_sender and not as_receiver:
            return []
        
        # Build match conditions
        if as_sender and as_receiver:
            match_stage = {"$or": [
                {"payments.sender.id": user_id},
                {"payments.receiver.id": user_id}
            ]}
        elif as_sender:
            match_stage = {"payments.sender.id": user_id}
        else:  # as_receiver only
            match_stage = {"payments.receiver.id": user_id}
        
        events = await database[self.collection_name].aggregate([
            {"$match": {"payments": {"$exists": True, "$ne": []}}},
            {"$unwind": "$payments"},
            {"$match": match_stage},
            {
                "$project": {
                    "event_id": {"$toString": "$_id"},
                    "event_name": "$name",
                    "payment": "$payments"
                }
            }
        ]).to_list(length=None)
        
        return events

    async def update_payment(self, event_id: str, payment_id: str, payment_update: PaymentUpdate) -> Optional[dict]:
        database = await get_database()
        
        update_data = jsonable_encoder(payment_update, exclude_unset=True)
        
        # Create the update expression for the nested payment
        set_expressions: Dict[str, Any] = {}
        for field, value in update_data.items():
            set_expressions[f"payments.$.{field}"] = value
        
        set_expressions["updated_at"] = datetime.utcnow()
        
        result = await database[self.collection_name].update_one(
            {"_id": ObjectId(event_id), "payments.id": payment_id},
            {"$set": set_expressions}
        )
        
        if result.modified_count:
            return await self.get_event_by_id(event_id)
        return None

    async def delete_payment(self, event_id: str, payment_id: str) -> Optional[dict]:
        database = await get_database()
        
        result = await database[self.collection_name].update_one(
            {"_id": ObjectId(event_id)},
            {
                "$pull": {"payments": {"id": payment_id}},
                "$set": {"updated_at": datetime.utcnow()},
            }
        )
        
        if result.modified_count:
            return await self.get_event_by_id(event_id)
        return None


payment_crud = PaymentCRUD()