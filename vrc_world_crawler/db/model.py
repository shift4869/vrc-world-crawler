import re
from pathlib import Path
from typing import Self

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class FavoriteWorld(Base):
    """FavoriteWorldモデル
    [id] INTEGER NOT NULL UNIQUE,
    [post_id] TEXT NOT NULL UNIQUE,
    [user_id] TEXT NOT NULL,
    [url] TEXT NOT NULL,
    [text] TEXT,
    [created_at] TEXT NOT NULL,
    [registered_at] TEXT NOT NULL,
    PRIMARY KEY([id])
    """

    __tablename__ = "FavoriteWorld"

    id = Column(Integer, primary_key=True)
    post_id = Column(String(256), nullable=False, unique=True)
    user_id = Column(String(256), nullable=False)
    url = Column(String(256), nullable=False)
    text = Column(String(512))
    created_at = Column(String(256), nullable=False)
    registered_at = Column(String(256), nullable=False)

    def __init__(self, post_id: str, user_id: str, url: str, text: str, created_at: str, registered_at: str):
        # self.id = id
        self.post_id = post_id
        self.user_id = user_id
        self.url = url
        self.text = text
        self.created_at = created_at
        self.registered_at = registered_at

    @classmethod
    def create(self, args_dict: dict) -> Self:
        match args_dict:
            case {
                "post_id": post_id,
                "user_id": user_id,
                "url": url,
                "text": text,
                "created_at": created_at,
                "registered_at": registered_at,
            }:
                return Like(post_id, user_id, url, text, created_at, registered_at)
            case _:
                raise ValueError("Unmatch args_dict.")

    def __repr__(self):
        return f"<Like(post_id='{self.post_id}')>"

    def __eq__(self, other):
        return isinstance(other, Like) and other.post_id == self.post_id

    def to_dict(self) -> dict:
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "url": self.url,
            "text": self.text,
            "created_at": self.created_at,
            "registered_at": self.registered_at,
        }


if __name__ == "__main__":
    engine = create_engine(f"sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)

    session = Session(engine)
    result = session.query(FavoriteWorld).all()

    session.close()
