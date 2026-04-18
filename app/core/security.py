import uuid
from enum import Enum
from jose import jwt
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext # type: ignore[call-arg]

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"

def hash_password(password: str) -> str:
    """Creates and returns a hased version of the password"""
    return pwd_context.hash(password)

def verify_password(raw_password: str, hashed_password: str) -> bool:
    """Verifies the user input againsed the hashed password and returns a boolean value"""
    return pwd_context.verify(raw_password, hashed_password)


def create_jwt_token(data: dict, type: TokenType) -> str:
    to_encode = data.copy()
    expiry = (
        timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRY_MINUTES)
        if type == TokenType.ACCESS
        else timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRY_DAYS)
    )

    to_encode.update({
        "exp": datetime.now(timezone.utc) + expiry,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
        "type": "access" if type == TokenType.ACCESS else "refresh"
    })

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
