from typing import Self

from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class FavoriteWorld(Base):
    """FavoriteWorldモデル"""

    __tablename__ = "FavoriteWorld"

    id = Column(Integer, primary_key=True)
    world_id = Column(String(256), nullable=False, unique=True)
    world_name = Column(String(256), nullable=False)
    world_url = Column(String(512), nullable=False)
    description = Column(String(512))
    author_id = Column(String(256), nullable=False)
    author_name = Column(String(256), nullable=False)
    favorite_id = Column(String(256), nullable=False)
    favorite_group = Column(String(256), nullable=False)
    is_favorited = Column(Boolean, nullable=False)
    release_status = Column(String(256), nullable=False)
    featured = Column(Integer, nullable=False)
    image_url = Column(String(512))
    thmbnail_image_url = Column(String(512))
    version = Column(Integer, nullable=False)
    star = Column(Integer, nullable=False)
    visit = Column(Integer, nullable=False)
    published_at = Column(String(256))
    lab_published_at = Column(String(256))
    created_at = Column(String(256), nullable=False)
    updated_at = Column(String(256), nullable=False)
    registered_at = Column(String(256), nullable=False)

    def __init__(
        self,
        world_id: str,
        world_name: str,
        world_url: str,
        description: str,
        author_id: str,
        author_name: str,
        favorite_id: str,
        favorite_group: str,
        is_favorited: bool,
        release_status: str,
        featured: str,
        image_url: str,
        thmbnail_image_url: str,
        version: int,
        star: int,
        visit: int,
        published_at: str,
        lab_published_at: str,
        created_at: str,
        updated_at: str,
        registered_at: str,
    ):
        # self.id = id
        self.world_id = world_id
        self.world_name = world_name
        self.world_url = world_url
        self.description = description
        self.author_id = author_id
        self.author_name = author_name
        self.favorite_id = favorite_id
        self.favorite_group = favorite_group
        self.is_favorited = is_favorited
        self.release_status = release_status
        self.featured = featured
        self.image_url = image_url
        self.thmbnail_image_url = thmbnail_image_url
        self.version = version
        self.star = star
        self.visit = visit
        self.published_at = published_at
        self.lab_published_at = lab_published_at
        self.created_at = created_at
        self.updated_at = updated_at
        self.registered_at = registered_at

    @classmethod
    def create(self, args_dict: dict) -> Self:
        match args_dict:
            case {
                "world_id": world_id,
                "world_name": world_name,
                "world_url": world_url,
                "description": description,
                "author_id": author_id,
                "author_name": author_name,
                "favorite_id": favorite_id,
                "favorite_group": favorite_group,
                "is_favorited": is_favorited,
                "release_status": release_status,
                "featured": featured,
                "image_url": image_url,
                "thmbnail_image_url": thmbnail_image_url,
                "version": version,
                "star": star,
                "visit": visit,
                "published_at": published_at,
                "lab_published_at": lab_published_at,
                "created_at": created_at,
                "updated_at": updated_at,
                "registered_at": registered_at,
            }:
                return FavoriteWorld(
                    world_id,
                    world_name,
                    world_url,
                    description,
                    author_id,
                    author_name,
                    favorite_id,
                    favorite_group,
                    is_favorited,
                    release_status,
                    featured,
                    image_url,
                    thmbnail_image_url,
                    version,
                    star,
                    visit,
                    published_at,
                    lab_published_at,
                    created_at,
                    updated_at,
                    registered_at,
                )
            case _:
                raise ValueError("Unmatch args_dict.")

    def __repr__(self):
        return f"<FavoriteWorld(world_id='{self.world_id}')>"

    def __eq__(self, other):
        return isinstance(other, FavoriteWorld) and other.world_id == self.world_id

    def to_dict(self) -> dict:
        return {
            "world_id": self.world_id,
            "world_name": self.world_name,
            "world_url": self.world_url,
            "description": self.description,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "favorite_id": self.favorite_id,
            "favorite_group": self.favorite_group,
            "is_favorited": self.is_favorited,
            "release_status": self.release_status,
            "featured": self.featured,
            "image_url": self.image_url,
            "thmbnail_image_url": self.thmbnail_image_url,
            "version": self.version,
            "star": self.star,
            "visit": self.visit,
            "published_at": self.published_at,
            "lab_published_at": self.lab_published_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "registered_at": self.registered_at,
        }


if __name__ == "__main__":
    engine = create_engine(f"sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)

    session = Session(engine)
    result = session.query(FavoriteWorld).all()

    session.close()
