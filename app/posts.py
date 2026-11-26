from typing import Annotated

from fastapi import APIRouter, Path

from app.auth import CurrentUser
from app.database import Database
from app.models import Post
from app.repository import Repository
from app.schemas import PostInput, PostView

router = APIRouter(prefix="/posts", tags=["Посты"])
PostId = Annotated[int, Path(gt=0, description="Номер поста")]


@router.get("", response_model=list[PostView], summary="Список постов")
def list_posts(db: Database):
    return Repository(db, Post).list()


@router.get("/{post_id}", response_model=PostView, summary="Один пост")
def read_post(post_id: PostId, db: Database):
    return Repository(db, Post).require(post_id)


@router.post("", status_code=201, response_model=PostView, summary="Создать пост")
def create_post(data: PostInput, db: Database, current_id: CurrentUser):
    with db.begin():
        return Repository(db, Post).create(data.model_dump())


@router.put("/{post_id}", response_model=PostView, summary="Заменить пост")
def update_post(post_id: PostId, data: PostInput, db: Database, current_id: CurrentUser):
    repository = Repository(db, Post)
    with db.begin():
        repository.require(post_id, lock=True)
        return repository.upsert(post_id, data.model_dump())


@router.delete("/{post_id}", status_code=204, summary="Удалить пост")
def delete_post(post_id: PostId, db: Database, current_id: CurrentUser):
    with db.begin():
        db.delete(Repository(db, Post).require(post_id, lock=True))
