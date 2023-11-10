from fastapi import FastAPI

from api.app.v1.router.elevator_router import router as elevator_router
from api.app.v1.scripts.create_tables import create_tables

#create tables
create_tables()

app = FastAPI()

app.include_router(elevator_router)
