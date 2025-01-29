import os
from functools import wraps

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, Users, VALID_ROLES, VALID_STATUSES
from logger_config import get_logger
from bot import bot


log = get_logger(__name__)  # get configured logger

try:
    load_dotenv()
    engine = create_engine(os.getenv("DATABASE_URL"))
    log.info("Engine created!")
except Exception as e:
    log.error(f"Engine not created! {e}")


# create tables
def init_db():
    Base.metadata.create_all(bind=engine)


Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def check_user_permissions(allowed_roles: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            tg_id = message.chat.id

            with Session() as session:
                user = session.query(Users).filter(
                    Users.tg_id == tg_id).one_or_none()

                if user and \
                        user.role in allowed_roles and \
                        user.status == "active":
                    return func(message, *args, **kwargs)

                else:
                    bot.send_message(
                        chat_id=tg_id,
                        text="You do not have permission for this command."
                    )
                    return
        return wrapper
    return decorator


def create_user(tg_id: int, name: str, role: str = "user") -> bool:
    """
    Creates new user in the database with the given Telegram ID.
    Return True if user was created, otherwise False
    """
    with Session() as session:
        user_exists = session.query(
            session.query(Users).filter(Users.tg_id == tg_id).exists()
        ).scalar()
        if not user_exists:
            new_user = Users(tg_id=tg_id, name=name, role=role)
            try:
                session.add(new_user)
                session.commit()
                log.info(f"User created: {tg_id=}, {name=}")
                return True

            except Exception as e:
                log.error(f"An error occurred while creating user: {e}")
                return False

        else:
            log.warning(f"User with {tg_id=} already exist!")
            return True


def init_user():
    """
    Initializes the first administrator user in the database. The user data is
    taken from the env 'INIT_ADMIN_USER'.
    """
    init_user = os.getenv("INIT_ADMIN_USER")
    if init_user:
        log.info(f"Init user found: {init_user=}.")
        try:
            tg_id, name = init_user.split(":")
            tg_id = int(tg_id)
            user_created = create_user(tg_id=tg_id, name=name, role="admin")
            if user_created:
                log.info("Init user created.")
            else:
                log.warning("Init user did not created.")
        except ValueError as e:
            log.error(f"Error during user {init_user} initialization: {e}.")
    else:
        log.info("Init user not found, skip this step.")


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
