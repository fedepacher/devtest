import peewee
from datetime import datetime

from api.app.v1.utils.db import db


class Elevator(peewee.Model):
    """DB Elevator columns definition.

    Args:
        peewee (_type_): Validation model.
    """
    next_floor = peewee.IntegerField()
    demand_floor = peewee.IntegerField()
    call_datetime = peewee.DateTimeField(default=datetime.now)
    
    class Meta:
        """DB connection"""
        database = db
