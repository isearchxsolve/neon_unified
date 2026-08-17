from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ..schemas.habit import HabitCreate, HabitUpdate, HabitResponse, HabitCompletionResponse
from ..services.habit_service import HabitService
from ..services.exceptions import NotFoundError, OwnershipError, ConflictError

router = APIRouter(prefix="/api/habits", tags=["habits"])

def get_habit_service() -> HabitService:
    return HabitService()

def handle_domain_exception(e: Exception) -> HTTPException:
    if isinstance(e, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if isinstance(e, OwnershipError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    if isinstance(e, ConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(
    payload: HabitCreate,
    user_id: int,
    service: HabitService = Depends(get_habit_service)
):
    try:
        return service.create_habit(user_id, payload)
    except Exception as e:
        raise handle_domain_exception(e)

@router.get("/", response_model=List[HabitResponse])
def list_habits(
    user_id: int,
    include_archived: bool = False,
    service: HabitService = Depends(get_habit_service)
):
    try:
        return service.list_habits(user_id, include_archived)
    except Exception as e:
        raise handle_domain_exception(e)

@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(
    habit_id: int,
    user_id: int,
    service: HabitService = Depends(get_habit_service)
):
    try:
        return service.get_habit(user_id, habit_id)
    except Exception as e:
        raise handle_domain_exception(e)

@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    payload: HabitUpdate,
    user_id: int,
    service: HabitService = Depends(get_habit_service)
):
    try:
        return service.update_habit(user_id, habit_id, payload)
    except Exception as e:
        raise handle_domain_exception(e)

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int,
    user_id: int,
    service: HabitService = Depends(get_habit_service)
):
    try:
        service.delete_habit(user_id, habit_id)
    except Exception as e:
        raise handle_domain_exception(e)

@router.post("/{habit_id}/complete", response_model=HabitCompletionResponse)
def mark_habit_complete(
    habit_id: int,
    user_id: int,
    service: HabitService = Depends(get_habit_service)
):
    try:
        return service.mark_complete(user_id, habit_id)
    except Exception as e:
        raise handle_domain_exception(e)

@router.get("/dashboard/summary", response_model=dict)
def get_dashboard(
    user_id: int,
    service: HabitService = Depends(get_habit_service)
):
    try:
        return service.get_dashboard_summary(user_id)
    except Exception as e:
        raise handle_domain_exception(e)