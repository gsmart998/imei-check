from sqlalchemy import Column, BigInteger, String, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from logger_config import get_logger


log = get_logger(__name__)  # get configured logger

VALID_ROLES = {"user", "admin"}
VALID_STATUSES = {"active", "disabled"}

Base = declarative_base()


class Users(Base):
    """
    tg_id use BigInteger for correct work with all user id.
    role: user role in the service ['user', 'admin']
        'user' - can use the service
        'admin' - can do the same, and can also add new users and delete them

    status: user status in the service ['active', 'disabled']
        'active' - can use the service
        'disabled' - can't do anything

    """
    __tablename__ = "users"
    tg_id: int = Column(BigInteger, primary_key=True,
                        unique=True, nullable=False)
    name: str = Column(String(50))
    role: str = Column(String(20), nullable=False, server_default="user")
    status: str = Column(String(20), nullable=False, server_default="active")
    last_update: str = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.current_timestamp()
    )

    # user_translations = relationship("UserTranslations", back_populates="user")

    def __init__(
        self,
        tg_id: int,
        name: str,
        role: str = "user",
        status: str = "active",
    ):
        if role not in VALID_ROLES:
            error_msg = f"Invalid role: {role}. Valid roles are: {VALID_ROLES}"
            log.error(error_msg)
            raise ValueError(error_msg)

        if status not in VALID_STATUSES:
            error_msg = f"Invalid status: {status}. Valid roles are: {
                VALID_STATUSES}"
            log.error(error_msg)
            raise ValueError(error_msg)

        self.tg_id = tg_id
        self.name = name
        self.role = role
        self.status = status
