import functools
import pprint
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Self

import orjson

from vrc_world_crawler.db.model import FavoriteWorld
from vrc_world_crawler.util import find_values, to_jst


@dataclass(frozen=True)
class FetchedInfo:
    world_id: str
    world_name: str
    world_url: str
    description: str
    author_id: str
    author_name: str
    favorite_id: str
    favorite_group: str
    release_status: str
    featured: int
    image_url: str
    thmbnail_image_url: str
    version: int
    star: int
    visit: int
    published_at: str
    lab_published_at: str
    created_at: str
    updated_at: str
    registered_at: str

    def __post_init__(self) -> None:
        """引数チェック
        Raises:
        """
        pass

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

    @classmethod
    def create(cls, fetched_dict: dict) -> Self:
        """fetched_info インスタンスを作成する

        fetch データの辞書解析を行う
        fetch データの辞書構造が変わった・取得情報の参照元が変わった場合はこのメソッドを更新する

        Args:
            fetched_dict (dict): fetch したデータ辞書の1レコード

        Returns:
            Self: fetched_info インスタンス
        """

        def normalize_date_at(date_at_str: str) -> str:
            """日時文字列を日本時間に変換する

            Args:
                date_at_str (str): ISOフォーマットの日時文字列(UTC)

            Returns:
                str: ISOフォーマットの日時文字列(JST)
            """
            result = to_jst(datetime.fromisoformat(date_at_str)).isoformat()
            if result.endswith("+00:00"):
                result = result[:-6]
            return result

        find = functools.partial(find_values, obj=fetched_dict, is_predict_one=True, key_white_list=[""])

        # fetch データの辞書解析
        world_id = find(key="id")
        world_name = find(key="name")
        world_url = f"https://vrchat.com/home/world/{world_id}"
        description = find(key="description")
        author_id = find(key="authorId")
        author_name = find(key="authorName")
        favorite_id = find(key="favoriteId")
        favorite_group = find(key="favoriteGroup")
        release_status = find(key="releaseStatus")
        featured = 1 if bool(find(key="featured")) else 0
        image_url = find(key="imageUrl")
        thmbnail_image_url = find(key="thumbnailImageUrl")
        version = int(find(key="version"))
        star = int(find(key="favorites"))
        visit = int(find(key="visits"))
        published_at_str = find(key="publicationDate")
        published_at = "" if published_at_str == "none" else normalize_date_at(published_at_str)
        lab_published_at_str = find(key="labsPublicationDate")
        lab_published_at = "" if lab_published_at_str == "none" else normalize_date_at(lab_published_at_str)
        created_at = normalize_date_at(find(key="created_at"))
        updated_at = normalize_date_at(find(key="updated_at"))
        registered_at = datetime.now().isoformat()

        return FetchedInfo(
            world_id,
            world_name,
            world_url,
            description,
            author_id,
            author_name,
            favorite_id,
            favorite_group,
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


if __name__ == "__main__":
    cache_path = Path("./cache/")
    last_cache_file: Path = max(cache_path.glob("*"), key=lambda path: path.stat().st_mtime)
    fetched_dict_list = orjson.loads(last_cache_file.read_bytes())
    for entry in fetched_dict_list[:3]:
        fetched_info = FetchedInfo.create(entry)
        pprint.pprint(fetched_info)
