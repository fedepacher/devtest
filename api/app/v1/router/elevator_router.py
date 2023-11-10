from datetime import datetime
from fastapi import APIRouter, Depends, Body, status, Query, Path
from typing import List, Optional

from api.app.v1.schema import elevator_schema
from api.app.v1.service import elevator_service
from api.app.v1.utils.db import get_db


router = APIRouter(prefix="/api/v1/elevator")

@router.post(
    "/",
    tags=["elevator"],
    status_code=status.HTTP_201_CREATED,
    response_model=elevator_schema.Elevator,
    dependencies=[Depends(get_db)]
)
def create_element(elevator: elevator_schema.Elevator=Body(...)):
    """Create element in the DB.

    Args:
        elevator (elevator_schema.Elevatorr): Element to be created.
        
    Returns:
        json: Elevator information created.
    """
    return elevator_service.create_element(elevator)


@router.get(
    "/",
    tags=["elevator"],
    status_code=status.HTTP_200_OK,
    response_model=List[elevator_schema.Elevator],
    dependencies=[Depends(get_db)]
)
def get_elements():
    """Get all DB elements.

    Returns:
        json: Elevator information.
    """
    return elevator_service.get_elements()


@router.get(
    "/{element_id}",
    tags=["elevator"],
    status_code=status.HTTP_200_OK,
    response_model=elevator_schema.Elevator,
    dependencies=[Depends(get_db)]
)
def get_element(element_id: int = Path(..., gt=0)):
    """Get element by ID in the DB.

    Args:
        element_id (int): Id to find.
        
    Returns:
        json: Elevator information by ID.
    """
    return elevator_service.get_element_by_id(element_id)


@router.patch(
    "/{element_id}",
    tags=["elevator"],
    status_code=status.HTTP_200_OK,
    response_model=elevator_schema.Elevator,
    dependencies=[Depends(get_db)]
)
def update_element(element_id: int = Path(..., gt=0),
                   next_floor: int=-1, demand_floor: int=-1, call_datetime: datetime=None):
    """Update element fields by ID.

    Args:
        element_id (int, optional): Element ID. Defaults to Path(..., gt=0).
        next_floor (int, optional): Next floor. Defaults to -1.
        demand_floor (int, optional): Demanding floor. Defaults to -1.
        call_datetime (datetime, optional): Call datetime. Defaults to None.

    Returns:
        json: Elevator information by ID.
    """
    return elevator_service.update_element(element_id, next_floor, demand_floor,
                                           call_datetime)


@router.delete(
    "/{element_id}",
    tags=["elevator"],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_db)]
)
def delete_element(element_id: int = Path(..., gt=0)):
    """Delete element by ID.

    Args:
        element_id (int): Element ID.
        
    Returns:
        json: Deleted element's message.
    """
    elevator_service.delete_element(element_id)

    return {'msg': f'Element {element_id} has been deleted successfully'}
