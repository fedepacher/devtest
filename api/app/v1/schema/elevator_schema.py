from datetime import datetime
from pydantic import BaseModel
from pydantic import Field


class Elevator(BaseModel):
    """Elevator DB schema

    Args:
        BaseModel (Any): Parameter checker.
    """
    id: int = Field(...)
    next_floor: int = Field(default=0)
    demand_floor: int = Field(default=0)
    call_datetime: datetime = Field(default=datetime.now())
