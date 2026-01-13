import datetime as dt

import jwt
from passlib.context import CryptContext

from .config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(subject: str, secret: str, minutes: int) -> str:
    payload = {
        "sub": subject,
        "exp": dt.datetime.utcnow() + dt.timedelta(minutes=minutes),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str, secret: str) -> str:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    return payload["sub"]


def create_access_token(user_id: int) -> str:
    return create_token(str(user_id), settings.jwt_secret, 60)


def create_refresh_token(user_id: int) -> str:
    return create_token(str(user_id), settings.refresh_secret, 60 * 24 * 7)
