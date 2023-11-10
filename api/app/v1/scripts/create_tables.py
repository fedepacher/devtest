from api.app.v1.model.elevator_model import Elevator
from api.app.v1.utils.db import db


def create_tables():
    """Create DB tables."""
    with db:
        db.create_tables([Elevator])
