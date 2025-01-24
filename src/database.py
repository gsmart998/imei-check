import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Users, VALID_ROLES, VALID_STATUSES
from logger_config import get_logger


log = get_logger(__name__)  # get configured logger

try:
    load_dotenv()
    engine = create_engine(os.getenv("DATABASE_URL"))
    log.info("Engine created!")
except Exception as ex:
    log.error(f"Engine not created! {ex}")


# create tables
def init_db():
    Base.metadata.create_all(bind=engine)


Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def create_user(tg_id: int, name: str) -> bool:
    """
    Creates new user in the database with the given Telegram ID.
    Return True if user was created, otherwise False
    """
    with Session() as session:
        user_exists = session.query(
            session.query(Users).filter(Users.tg_id == tg_id).exists()
        ).scalar()
        if not user_exists:
            new_user = Users(tg_id=tg_id, name=name)
            try:
                session.add(new_user)
                session.commit()
                log.info(f"User created: {tg_id=}, {name=}")
                return True

            except Exception as ex:
                log.error(f"An error occurred while creating user: {ex}")
                return False

        else:
            log.warning(f"User with {tg_id=} already exist!")
            return True


def is_user_admin(tg_id: int) -> bool:
    """
    Checks if user with the given Telegram ID has an admin role and an active
    status.
    """
    with Session() as session:
        user = session.query(Users).filter(Users.tg_id == tg_id).one_or_none()
        if not user or user.role != "admin" or user.status != "active":
            return False
        return True


def is_user_active(tg_id: int) -> bool:
    """
    Checks if user with the given Telegram ID has an active status.
    """
    with Session() as session:
        user = session.query(Users).filter(Users.tg_id == tg_id).one_or_none()
        if not user or user.status != "active":
            return False
        return True


def update_user(
    tg_id: int,
    new_role: str = None,
    new_status: str = None,
) -> bool:
    """
    Updates the role and/or status of a user by their Telegram ID.
    Return True if the user was updated successfully, False otherwise.
    """
    if new_role is None and new_status is None:
        log.warning("No updates specified for user.")
        return False

    with Session() as session:
        user: Users = session.query(Users).filter(
            Users.tg_id == tg_id).one_or_none()
        if not user:
            log.warning(f"User {tg_id} not found.")
            return False

        if new_role is not None:
            if new_role not in VALID_ROLES:
                log.warning(f"Invalid role provided: {new_role}")
                return False
            user.role = new_role
            log.info(f"Updated {tg_id=} with new role: {new_role}")

        if new_status is not None:
            if new_status not in VALID_STATUSES:
                log.warning(f"Invalid status provided: {new_status}")
                return False
            user.status = new_status
            log.info(f"Updated {tg_id=} with new status: {new_status}")

        session.commit()
        log.info(f"User {tg_id} updated.")
        return True
