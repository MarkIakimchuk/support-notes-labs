from itertools import count
from threading import Lock
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.schemas import PostInput, PostView

router = APIRouter(prefix="/posts", tags=["Посты"])
PostId = Annotated[int, Path(gt=0, description="Номер поста")]
posts: dict[int, PostView] = {}
numbers = count(1)
lock = Lock()


@router.get("", response_model=list[PostView], summary="Список постов")
def list_posts():
    with lock:
        return list(posts.values())


@router.get("/{post_id}", response_model=PostView, summary="Один пост")
def read_post(post_id: PostId):
    with lock:
        post = posts.get(post_id)
        if post is None:
            raise HTTPException(404, "Пост не найден")
        return post


@router.post("", status_code=201, response_model=PostView, summary="Создать пост")
def create_post(data: PostInput):
    with lock:
        post = PostView(id=next(numbers), **data.model_dump())
        posts[post.id] = post
        return post


@router.put("/{post_id}", response_model=PostView, summary="Заменить пост")
def update_post(post_id: PostId, data: PostInput):
    with lock:
        if post_id not in posts:
            raise HTTPException(404, "Пост не найден")
        post = PostView(id=post_id, **data.model_dump())
        posts[post_id] = post
        return post


@router.delete("/{post_id}", status_code=204, summary="Удалить пост")
def delete_post(post_id: PostId):
    with lock:
        if posts.pop(post_id, None) is None:
            raise HTTPException(404, "Пост не найден")
