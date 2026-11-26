from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID, uuid4

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Database, session_factory, settings
from app.models import AccessToken, RefreshToken, User
from app.schemas import Credentials, RefreshInput, TokenPair

router = APIRouter(prefix="/auth", tags=["Сессии"])
bearer = HTTPBearer(auto_error=False)
algorithm = "HS256"
issuer = "support-notes"
dummy_hash = bcrypt.hashpw(b"unused-password", bcrypt.gensalt())


def unauthorized():
    return HTTPException(401, "Неверные учётные данные или токен", headers={"WWW-Authenticate": "Bearer"})


def encode_token(key: UUID, user_id: int, kind: str, expiration: datetime):
    return jwt.encode(
        {"jti": str(key), "sub": str(user_id), "kind": kind, "exp": expiration, "iss": issuer},
        settings.jwt_secret,
        algorithm=algorithm,
    )


def decode_token(token: str, kind: str) -> tuple[UUID, int]:
    try:
        claims = jwt.decode(
            token, settings.jwt_secret, algorithms=[algorithm], issuer=issuer,
            options={"require": ["jti", "sub", "kind", "exp", "iss"]},
        )
        if claims["kind"] != kind:
            raise unauthorized()
        return UUID(claims["jti"]), int(claims["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError) as error:
        raise unauthorized() from error


class TokenController:
    def __init__(self, db: Session):
        self.db = db

    def issue(self, user_id: int):
        now = datetime.now(UTC)
        refresh = RefreshToken(id=uuid4(), user_id=user_id, expires_at=now + timedelta(days=7))
        access = AccessToken(id=uuid4(), refresh_id=refresh.id, expires_at=now + timedelta(minutes=15))
        self.db.add(refresh)
        self.db.flush()
        self.db.add(access)
        return TokenPair(
            access_token=encode_token(access.id, user_id, "access", access.expires_at),
            refresh_token=encode_token(refresh.id, user_id, "refresh", refresh.expires_at),
        )

    def revoke(self, token: str):
        key, user_id = decode_token(token, "refresh")
        session = self.db.get(RefreshToken, key, with_for_update=True)
        if session is None or session.user_id != user_id or session.expires_at <= datetime.now(UTC):
            raise unauthorized()
        self.db.delete(session)
        self.db.flush()
        return user_id

    def identify(self, token: str):
        key, user_id = decode_token(token, "access")
        now = datetime.now(UTC)
        active_user_id = self.db.scalar(
            select(RefreshToken.user_id)
            .join(AccessToken, AccessToken.refresh_id == RefreshToken.id)
            .where(AccessToken.id == key, AccessToken.expires_at > now, RefreshToken.expires_at > now)
        )
        if active_user_id != user_id:
            raise unauthorized()
        return user_id


class AuthController:
    def __init__(self, db: Session):
        self.db = db
        self.tokens = TokenController(db)

    def login(self, data: Credentials):
        user = self.db.scalar(select(User).where(User.username == data.username))
        password_hash = user.password_hash.encode() if user and user.password_hash else dummy_hash
        valid = bcrypt.checkpw(data.password.encode(), password_hash)
        if not valid or not user or not user.password_hash:
            raise unauthorized()
        return self.tokens.issue(user.id)


def current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if credentials is None:
        raise unauthorized()
    with session_factory() as db:
        return TokenController(db).identify(credentials.credentials)


CurrentUser = Annotated[int, Depends(current_user)]


@router.post("/login", response_model=TokenPair)
def login(data: Credentials, db: Database):
    with db.begin():
        return AuthController(db).login(data)


@router.get("/verify")
def verify(user_id: CurrentUser):
    return {"user_id": user_id}


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshInput, db: Database):
    with db.begin():
        controller = TokenController(db)
        return controller.issue(controller.revoke(data.refresh_token))


@router.post("/logout", status_code=204)
def logout(data: RefreshInput, db: Database):
    with db.begin():
        TokenController(db).revoke(data.refresh_token)
