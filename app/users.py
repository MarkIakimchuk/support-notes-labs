from typing import Annotated

import bcrypt
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser
from app.database import Database
from app.models import User
from app.repository import Repository
from app.schemas import Registration, UserInput, UserView

router = APIRouter(prefix="/users", tags=["Пользователи"])
UserId = Annotated[int, Path(gt=0)]


class UserController:
    def __init__(self, db: Session):
        self.db = db
        self.repository = Repository(db, User)

    def create(self, data: Registration):
        password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
        try:
            with self.db.begin():
                return self.repository.create({
                    "username": data.username, "display_name": data.display_name,
                    "password_hash": password_hash,
                })
        except IntegrityError as error:
            raise HTTPException(409, "Имя пользователя занято") from error

    def update(self, key: int, data: UserInput):
        try:
            with self.db.begin():
                self.repository.require(key, lock=True)
                return self.repository.upsert(key, data.model_dump())
        except IntegrityError as error:
            raise HTTPException(409, "Имя пользователя занято") from error

    def delete(self, key: int):
        with self.db.begin():
            self.db.delete(self.repository.require(key, lock=True))


@router.get("", response_model=list[UserView])
def list_users(db: Database):
    return UserController(db).repository.list()


@router.get("/{user_id}", response_model=UserView)
def read_user(user_id: UserId, db: Database):
    return UserController(db).repository.require(user_id)


@router.post("", status_code=201, response_model=UserView)
def create_user(data: Registration, db: Database):
    return UserController(db).create(data)


@router.put("/{user_id}", response_model=UserView)
def update_user(user_id: UserId, data: UserInput, db: Database, current_id: CurrentUser):
    if user_id != current_id:
        raise HTTPException(403, "Можно менять только свой профиль")
    return UserController(db).update(user_id, data)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: UserId, db: Database, current_id: CurrentUser):
    if user_id != current_id:
        raise HTTPException(403, "Можно удалить только свой профиль")
    UserController(db).delete(user_id)
