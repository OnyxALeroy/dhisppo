from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from app.core.database import get_database
from app.schemas.event import EventCreate, EventUpdate, Participant


class EventCRUD:
    def __init__(self):
        self.collection_name = "events"

    async def create_event(self, event_data: EventCreate) -> dict:
        database = await get_database()
        # Use jsonable_encoder to convert date/time objects to strings
        # This fixes the "bson.errors.InvalidDocument" error
        event_dict = jsonable_encoder(event_data)
        
        # Ensure payments and participants arrays exist
        if "payments" not in event_dict:
            event_dict["payments"] = []
        if "participants" not in event_dict:
            event_dict["participants"] = []
        
        # Add timestamps as real datetime objects (MongoDB handles these fine)
        event_dict["created_at"] = datetime.utcnow()
        event_dict["updated_at"] = datetime.utcnow()

        result = await database[self.collection_name].insert_one(event_dict)
        
        # Return the actual document from MongoDB to ensure all fields are present
        return await database[self.collection_name].find_one({"_id": result.inserted_id})

    async def get_event_by_id(self, event_id: str) -> Optional[dict]:
        database = await get_database()
        event = await database[self.collection_name].find_one(
            {"_id": ObjectId(event_id)}
        )
        if event and "payments" not in event:
            event["payments"] = []
        if event and "participants" not in event:
            event["participants"] = []
        if event and "expenditures" not in event:
            event["expenditures"] = []
        if event and "visibility" not in event:
            event["visibility"] = "public"
        return event

    async def can_user_join(
        self, event_id: str, user_id: str, username: str, role: str
    ) -> tuple[bool, str]:
        event = await self.get_event_by_id(event_id)
        if not event:
            return False, "Event not found"
        
        visibility = event.get("visibility", "public")
        organizers = event.get("organizers", [])
        participants = event.get("participants", [])
        participant_ids = [p.get("user_id") for p in participants]
        
        if visibility == "public":
            return True, "Public event"
        
        if role == "admin":
            return True, "Admin access"
        
        if username in organizers:
            return True, "Organizer access"
        
        if user_id in participant_ids:
            return True, "Already a participant"
        
        return False, "Private event - invitation required"

    async def get_events(self, skip: int = 0, limit: int = 100) -> List[dict]:
        database = await get_database()
        events = (
            await database[self.collection_name]
            .find({"visibility": "public"})
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
        for event in events:
            if "payments" not in event:
                event["payments"] = []
            if "participants" not in event:
                event["participants"] = []
            if "expenditures" not in event:
                event["expenditures"] = []
        return events

    async def get_events_for_user(
        self, user_id: str, username: str, role: str, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        database = await get_database()
        
        if role == "admin":
            events = (
                await database[self.collection_name]
                .find()
                .skip(skip)
                .limit(limit)
                .to_list(length=limit)
            )
        else:
            events = (
                await database[self.collection_name]
                .find({
                    "$or": [
                        {"visibility": "public"},
                        {"organizers": username},
                        {"participants.user_id": user_id}
                    ]
                })
                .skip(skip)
                .limit(limit)
                .to_list(length=limit)
            )
        
        for event in events:
            if "payments" not in event:
                event["payments"] = []
            if "participants" not in event:
                event["participants"] = []
            if "expenditures" not in event:
                event["expenditures"] = []
            if "visibility" not in event:
                event["visibility"] = "public"
        return events

    async def get_events_by_organizer(
        self, organizer: str, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        database = await get_database()
        events = (
            await database[self.collection_name]
            .find({"organizers": organizer})
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
        for event in events:
            if "payments" not in event:
                event["payments"] = []
            if "participants" not in event:
                event["participants"] = []
            if "expenditures" not in event:
                event["expenditures"] = []
        return events

    async def get_events_by_location(
        self, location: str, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        database = await get_database()
        events = (
            await database[self.collection_name]
            .find({"locations": location})
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
        for event in events:
            if "payments" not in event:
                event["payments"] = []
            if "participants" not in event:
                event["participants"] = []
            if "expenditures" not in event:
                event["expenditures"] = []
        return events

    async def update_event(
        self, event_id: str, event_update: EventUpdate
    ) -> Optional[dict]:
        database = await get_database()
        # Use jsonable_encoder to convert date/time objects to strings
        # This fixes the "bson.errors.InvalidDocument" error
        update_data = jsonable_encoder(event_update, exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        result = await database[self.collection_name].update_one(
            {"_id": ObjectId(event_id)}, {"$set": update_data}
        )

        if result.modified_count:
            return await self.get_event_by_id(event_id)
        return None

    async def add_participant(
        self, event_id: str, participant: Participant
    ) -> Optional[dict]:
        database = await get_database()

        result = await database[self.collection_name].update_one(
            {"_id": ObjectId(event_id)},
            {
                "$push": {"participants": jsonable_encoder(participant)},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )

        if result.modified_count:
            return await self.get_event_by_id(event_id)
        return None

    async def remove_participant(self, event_id: str, user_id: str) -> Optional[dict]:
        database = await get_database()

        result = await database[self.collection_name].update_one(
            {"_id": ObjectId(event_id)},
            {
                "$pull": {"participants": {"user_id": user_id}},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )

        if result.modified_count:
            return await self.get_event_by_id(event_id)
        return None

    async def update_participant_payment(
        self, event_id: str, user_id: str, paid_amount: float
    ) -> Optional[dict]:
        database = await get_database()

        result = await database[self.collection_name].update_one(
            {"_id": ObjectId(event_id), "participants.user_id": user_id},
            {
                "$set": {
                    "participants.$.paid_amount": paid_amount,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.modified_count:
            return await self.get_event_by_id(event_id)
        return None

    async def delete_event(self, event_id: str) -> bool:
        database = await get_database()
        result = await database[self.collection_name].delete_one(
            {"_id": ObjectId(event_id)}
        )
        return result.deleted_count > 0


event_crud = EventCRUD()
