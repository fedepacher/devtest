import os
os.environ['RUN_ENV'] = 'test'

from api.app.v1.model import elevator_model
from api.app.v1.utils.settings import Settings

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

settings = Settings()


def postgresql_connection():
    """Create connection to DB.

    Returns:
        connection: Connection.
    """
    con = psycopg2.connect(f"dbname='postgres' host='{settings.db_host}' port='{settings.db_port}' user='{settings.db_user}' password='{settings.db_pass}'")

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return con


def delete_database():
    """Delete DB if exists.

    Raises:
        Exception: if DB does not start with test.
    """
    if not settings.db_name.startswith("test_"):
        raise Exception(f'Invalid name for database = {settings.db_name}')

    sql_drop_db = f"DROP DATABASE IF EXISTS {settings.db_name}"
    con = postgresql_connection()
    cursor = con.cursor()
    cursor.execute("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity " \
                   f"WHERE pg_stat_activity.datname = '{settings.db_name}' " \
                   "AND pid <> pg_backend_pid();")
    cursor.execute(sql_drop_db)
    con.close()


def create_database():
    """Create DB."""
    sql_create_db = f"CREATE DATABASE {settings.db_name} WITH OWNER = {settings.db_user} " \
                    "ENCODING = 'UTF8' CONNECTION LIMIT = -1;"

    con = postgresql_connection()
    cursor = con.cursor()
    cursor.execute(sql_create_db)
    con.close()


def pytest_sessionstart(session):
    """Start tests session.

    Args:
        session (_type_): Session
    """
    delete_database()
    create_database()

    from api.app.v1.utils.db import db

    with db:
        db.create_tables([elevator_model.Elevator])


def pytest_sessionfinish(session, exitstatus):
    """End tests session.

    Args:
        session (_type_): Session.
        exitstatus (_type_): Status.
    """
    delete_database()
