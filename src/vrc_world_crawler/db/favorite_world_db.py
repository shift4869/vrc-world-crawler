from logging import INFO, getLogger

from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from vrc_world_crawler.db.base import Base
from vrc_world_crawler.db.model import FavoriteWorld

logger = getLogger(__name__)
logger.setLevel(INFO)


class FavoriteWorldDB(Base):
    def __init__(self, db_path: str = "vrc.db"):
        super().__init__(db_path)

    def select(self):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        result = session.query(FavoriteWorld).all()
        session.close()
        return result

    def upsert(self, record: FavoriteWorld | list[FavoriteWorld]) -> list[int]:
        """upsert

        Args:
            record (FavoriteWorld | list[FavoriteWorld]): 投入レコード、またはレコード辞書のリスト

        Returns:
            list[int]: レコードに対応した投入結果のリスト
                       追加したレコードは0、更新したレコードは1が入る
        """
        result: list[int] = []
        record_list: list[FavoriteWorld] = []
        match record:
            case FavoriteWorld():
                record_list = [record]
            case [FavoriteWorld(), *rest] if all([isinstance(r, FavoriteWorld) for r in rest]):
                record_list = record
            case _:
                raise TypeError("record is invalid type.")

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        for r in record_list:
            if r.release_status == "public":
                try:
                    q = (
                        session.query(FavoriteWorld)
                        .filter(and_(FavoriteWorld.world_id == r.world_id))
                        .with_for_update()
                    )
                    p = q.one()
                except NoResultFound:
                    # INSERT
                    session.add(r)
                    logger.info(f"Add World: {r.world_name}")
                    result.append(0)
                else:
                    # UPDATE
                    p.world_id = r.world_id
                    p.world_name = r.world_name
                    p.world_url = r.world_url
                    p.description = r.description
                    p.author_id = r.author_id
                    p.author_name = r.author_name
                    p.favorite_id = r.favorite_id
                    p.favorite_group = r.favorite_group
                    p.release_status = r.release_status
                    p.featured = r.featured
                    p.image_url = r.image_url
                    p.thmbnail_image_url = r.thmbnail_image_url
                    p.version = r.version
                    p.star = r.star
                    p.visit = r.visit
                    p.published_at = r.published_at
                    p.lab_published_at = r.lab_published_at
                    p.created_at = r.created_at
                    p.updated_at = r.updated_at
                    # p.registered_at = r.registered_at
                    result.append(1)
            else:
                try:
                    q = (
                        session.query(FavoriteWorld)
                        .filter(and_(FavoriteWorld.favorite_id == r.favorite_id))
                        .with_for_update()
                    )
                    p = q.one()
                except NoResultFound:
                    # 対象 favorite_id が見つからなかった場合 INSERT はしない
                    pass
                    result.append(0)
                else:
                    # UPDATE
                    if p.release_status != r.release_status:
                        p.favorite_id = r.favorite_id
                        p.favorite_group = r.favorite_group
                        p.release_status = r.release_status
                        p.registered_at = r.registered_at
                        msg = f"release_status from '{p.release_status}' to '{r.release_status}'"
                        logger.info(f"Change {msg}, World: {p.world_name}")
                    result.append(1)

        session.commit()
        session.close()
        return result
