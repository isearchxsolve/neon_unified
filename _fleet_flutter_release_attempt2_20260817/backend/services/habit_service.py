"""
Service layer for Habit business logic.
"""
from __future__ import annotations

import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import UploadFile
from pydantic import BaseModel, Field, field_validator

# Assuming these might be imported from app.schemas or app.models in a real project
# For standalone completeness, they are defined here.

class Habit(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str
    description: Optional[str] = None
    target_frequency: str = "daily"
    completed_dates: list[datetime.date] = Field(default_factory=list)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Config:
        from_attributes = True

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_frequency: str = "daily"

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Habit name cannot be empty")
        return v.strip()

    @field_validator("target_frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        allowed = ["daily", "weekly", "monthly"]
        if v not in allowed:
            raise ValueError(f"Invalid frequency. Must be one of {allowed}")
        return v

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_frequency: Optional[str] = None
    add_completion_date: Optional[datetime.date] = None
    remove_completion_date: Optional[datetime.date] = None

# --- Domain-Specific Exceptions ---

class HabitNotFound(Exception):
    """Raised when a habit is not found in the repository."""
    pass

class ValidationError(Exception):
    """Raised when input data fails business validation."""
    pass


# --- Repository Protocol (for in-memory mock / SQLAlchemy mocking) ---

class IHabitRepository:
    async def get_by_id(self, habit_id: UUID) -> Optional[Habit]:
        raise NotImplementedError

    async def list_by_user(self, user_id: UUID) -> list[Habit]:
        raise NotImplementedError

    async def add(self, habit: Habit) -> Habit:
        raise NotImplementedError

    async def update(self, habit: Habit) -> Habit:
        raise NotImplementedError

    async def delete(self, habit_id: UUID) -> bool:
        raise NotImplementedError


class InMemoryHabitRepository(IHabitRepository):
    """Simple in-memory implementation for testing/development."""
    def __init__(self):
        self._db: dict[UUID, Habit] = {}

    async def get_by_id(self, habit_id: UUID) -> Optional[Habit]:
        return self._db.get(habit_id)

    async def list_by_user(self, user_id: UUID) -> list[Habit]:
        return [h for h in self._db.values() if h.user_id == user_id]

    async def add(self, habit: Habit) -> Habit:
        self._db[habit.id] = habit
        return habit

    async def update(self, habit: Habit) -> Habit:
        if habit.id not in self._db:
            return None
        self._db[habit.id] = habit
        return habit

    async def delete(self, habit_id: UUID) -> bool:
        if habit_id in self._db:
            del self._db[habit_id]
            return True
        return False


class HabitService:
    """
    Handles business logic for Habits including CRUD and completion tracking.
    Routers delegate to this service. Services handle domain rules and interact with repositories.
    """
    
    def __init__(self, repository: IHabitRepository):
        self.repository = repository

    async def list_habits(self, user_id: UUID) -> list[Habit]:
        """Retrieve all habits for a specific user."""
        return await self.repository.list_by_user(user_id)

    async def get_habit(self, user_id: UUID, habit_id: UUID) -> Habit:
        """Retrieve a single habit, ensuring it belongs to the user."""
        habit = await self.repository.get_by_id(habit_id)
        if not habit or habit.user_id != user_id:
            raise HabitNotFound(f"Habit with id {habit_id} not found for user.")
        return habit

    async def create_habit(self, user_id: UUID, habit_data: HabitCreate) -> Habit:
        """Create a new habit validating business rules."""
        # Pydantic validation
        try:
            validated_data = habit_data.model_dump()
        except Exception as e:
            raise ValidationError(str(e))

        new_habit = Habit(
            user_id=user_id,
            name=validated_data["name"],
            description=validated_data.get("description", ""),
            target_frequency=validated_data["target_frequency"],
            completed_dates=[]
        )
        
        return await self.repository.add(new_habit)

    async def update_habit(self, user_id: UUID, habit_id: UUID, update_data: HabitUpdate) -> Habit:
        """Update habit metadata or mark/unmark completion."""
        habit = await self.get_habit(user_id, habit_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Handle name update
        if "name" in update_dict:
            if not update_dict["name"] or not update_dict["name"].strip():
                raise ValidationError("Name cannot be empty.")
            habit.name = update_dict["name"].strip()

        # Handle description update
        if "description" in update_dict and update_dict["description"] is not None:
            habit.description = update_dict["description"]

        # Handle frequency update
        if "target_frequency" in update_dict and update_dict["target_frequency"] is not None:
            allowed = ["daily", "weekly", "monthly"]
            if update_dict["target_frequency"] not in allowed:
                raise ValidationError(f"Invalid frequency. Must be one of {allowed}")
            habit.target_frequency = update_dict["target_frequency"]

        # Handle marking complete (append date)
        if "add_completion_date" in update_dict and update_dict["add_completion_date"] is not None:
            date_to_add = update_dict["add_completion_date"]
            if date_to_add > datetime.date.today():
                raise ValidationError("Cannot mark future dates as complete.")
            if date_to_add not in habit.completed_dates:
                habit.completed_dates.append(date_to_add)
                habit.completed_dates.sort()

        # Handle unmarking complete (remove date)
        if "remove_completion_date" in update_dict and update_dict["remove_completion_date"] is not None:
            date_to_remove = update_dict["remove_completion_date"]
            if date_to_remove in habit.completed_dates:
                habit.completed_dates.remove(date_to_remove)

        habit.updated_at = datetime.datetime.utcnow()
        
        return await self.repository.update(habit)

    async def delete_habit(self, user_id: UUID, habit_id: UUID) -> bool:
        """Delete a habit if it belongs to the user."""
        # get_habit will raise HabitNotFound if it doesn't exist or doesn't belong to user
        await self.get_habit(user_id, habit_id)
        return await self.repository.delete(habit_id)