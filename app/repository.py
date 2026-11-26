from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database import Base


class Repository[Model: Base]:
    def __init__(self, db: Session, model: type[Model]):
        self.db = db
        self.model = model

    def list(self):
        return list(self.db.scalars(select(self.model).order_by(self.model.id)))

    def require(self, key: int, *, lock: bool = False):
        record = self.db.get(self.model, key, with_for_update=lock)
        if record is None:
            raise HTTPException(404, "Запись не найдена")
        return record

    def create(self, values: dict):
        record = self.model(**values)
        self.db.add(record)
        self.db.flush()
        return record

    def upsert(self, key: int, values: dict):
        statement = insert(self.model).values(id=key, **values)
        statement = statement.on_conflict_do_update(
            index_elements=["id"],
            set_={name: statement.excluded[name] for name in values},
        )
        return self.db.scalars(
            statement.returning(self.model),
            execution_options={"populate_existing": True},
        ).one()
