import json

from fastapi import HTTPException, status
from datetime import datetime

from api.app.v1.schema import elevator_schema
from api.app.v1.model.elevator_model import Elevator as ElevatorModel


def create_element(element: elevator_schema.Elevator):
    """Create a new entrance in the database.

    Args:
        element (elevator_schema.CommentsCreate): Entrance to add to the DB.

    Returns:
        elevator_schema.Elevator: Entrance fields schema.
    """
    db_element = ElevatorModel(
        next_floor=element.next_floor,
        demand_floor=element.demand_floor,
        call_datetime=element.call_datetime,
    )

    db_element.save()

    return elevator_schema.Elevator(
        id=db_element.id,
        next_floor=db_element.next_floor,
        demand_floor=db_element.demand_floor,
        call_datetime=db_element.call_datetime
    )


def get_elements():
    """Get all the user's entrance in the DB.

    Returns:
        list: List of entrance filtered by user.
    """
    elements_by_user = ElevatorModel.filter().order_by(ElevatorModel.call_datetime.desc())

    elements_list = []
    for element in elements_by_user:
        elements_list.append(elevator_schema.Elevator(
            id=element.id,
            next_floor=element.next_floor,
            demand_floor=element.demand_floor,
            call_datetime=element.call_datetime
        ))

    return elements_list


def get_element_by_id(element_id: int):
    """Get user's entrance by ID in the DB.

    Args:
        element_id (int): ID of the entrance.

    Returns:
        elevator_schema.Elevator: Entrance fields schema.
    """
    elements_by_id = ElevatorModel.filter((ElevatorModel.id == element_id)).first()

    if not elements_by_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Element {element_id} not found'
        )

    return elevator_schema.Elevator(
        id=elements_by_id.id,
        next_floor=elements_by_id.next_floor,
        demand_floor=elements_by_id.demand_floor,
        call_datetime=elements_by_id.call_datetime
    )


def update_element(element_id: int, next_floor: int=-1,
                   demand_floor: int=-1, call_datetime: datetime=None):
    """Upadte element by ID.

    Args:
        element_id (int): Element ID.
        next_floor (int, optional): Next floor. Defaults to -1.
        demand_floor (int, optional): Demanding floor. Defaults to -1.
        call_datetime (datetime, optional): Call datetime. Defaults to None.

    Raises:
        HTTPException: If element was not found.

    Returns:
        elevator_schema.Elevator: Updated entrance fields schema.
    """
    element = ElevatorModel.filter((ElevatorModel.id == element_id)).first()

    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Element not found"
        )

    if next_floor != -1:
        element.next_floor = next_floor
    if demand_floor != -1:
        element.demand_floor = demand_floor
    if call_datetime is not None:
        element.call_datetime = call_datetime
    element.save()

    return elevator_schema.Elevator(
        id=element.id,
        next_floor=element.next_floor,
        demand_floor=element.demand_floor,
        call_datetime=element.call_datetime,
    )


def delete_element(element_id: int):
    """Delete element by ID

    Args:
        element_id (int): Element ID.

    Raises:
        HTTPException: If element was not found.
    """
    element = ElevatorModel.filter((ElevatorModel.id == element_id)).first()
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Element {element_id} not found'
        )

    element.delete_instance()
