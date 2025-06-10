import functools
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
        Raises: ValueError
        """
        if not isinstance(self.world_id, str):
            raise ValueError("world_id must be str.")
        if not isinstance(self.world_name, str):
            raise ValueError("world_name must br str")
        if not isinstance(self.world_url, str):
            raise ValueError("world_url must br str")
        if not isinstance(self.description, str):
            raise ValueError("description must br str")
        if not isinstance(self.author_id, str):
            raise ValueError("author_id must br str")
        if not isinstance(self.author_name, str):
            raise ValueError("author_name must br str")
        if not isinstance(self.favorite_id, str):
            raise ValueError("favorite_id must br str")
        if not isinstance(self.favorite_group, str):
            raise ValueError("favorite_group must br str")
        if not isinstance(self.release_status, str):
            raise ValueError("release_status must br str")
        if not isinstance(self.featured, int):
            raise ValueError("featured must br int")
        if not isinstance(self.image_url, str):
            raise ValueError("image_url must br str")
        if not isinstance(self.thmbnail_image_url, str):
            raise ValueError("thmbnail_image_url must br str")
        if not isinstance(self.version, int):
            raise ValueError("version must br int")
        if not isinstance(self.star, int):
            raise ValueError("star must br int")
        if not isinstance(self.visit, int):
            raise ValueError("visit must br int")
        if not isinstance(self.published_at, str):
            raise ValueError("published_at must br str")
        if not isinstance(self.lab_published_at, str):
            raise ValueError("lab_published_at must br str")
        if not isinstance(self.created_at, str):
            raise ValueError("created_at must br str")
        if not isinstance(self.updated_at, str):
            raise ValueError("updated_at must br str")
        if not isinstance(self.registered_at, str):
            raise ValueError("registered_at must br str")

        # world_id フォーマットチェック
        if self.release_status == "public":
            if not re.search("wrld_.*", self.world_id):
                raise ValueError("world_id must be 'wrld_.*'.")
        else:
            if self.world_id != "???":
                raise ValueError("Not available world_id must be '???'.")

        # 日付系フォーマットチェック
        # 空、もしくはISOフォーマットの文字列のみ受け付ける
        if self.published_at:
            datetime.fromisoformat(self.published_at)
        if self.lab_published_at:
            datetime.fromisoformat(self.lab_published_at)
        if self.created_at:
            datetime.fromisoformat(self.created_at)
        if self.updated_at:
            datetime.fromisoformat(self.updated_at)
        if self.registered_at:
            datetime.fromisoformat(self.registered_at)

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
        """FetchedInfo インスタンスを作成する

        fetch データの辞書解析を行う
        fetch データの辞書構造が変わった・取得情報の参照元が変わった場合はこのメソッドを更新する

        Args:
            fetched_dict (dict): fetch したデータ辞書の1レコード

        Returns:
            Self: FetchedInfo インスタンス
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

        registered_at = datetime.now().isoformat()
        find = functools.partial(find_values, obj=fetched_dict, is_predict_one=True, key_white_list=[""])

        # fetch データの辞書解析
        release_status = find(key="releaseStatus")
        if release_status != "public":
            # release_status が "public" でない場合
            # 現在公開されていないワールドの可能性が高い
            # 取得できる情報のみ取得する
            # ただし world_id, world_name, author_name は "???" となっているため実質的に情報を持たない
            # favorite_id は有効なのでこれで紐づける
            world_id = find(key="id")
            world_name = find(key="name")
            author_name = find(key="authorName")
            favorite_id = find(key="favoriteId")
            favorite_group = find(key="favoriteGroup")
            return FetchedInfo(
                world_id,
                world_name,
                "",
                "",
                "",
                author_name,
                favorite_id,
                favorite_group,
                release_status,
                -1,
                "",
                "",
                -1,
                -1,
                -1,
                "",
                "",
                "",
                "",
                registered_at,
            )

        world_id = find(key="id")
        world_name = find(key="name")
        world_url = f"https://vrchat.com/home/world/{world_id}"
        description = find(key="description")
        author_id = find(key="authorId")
        author_name = find(key="authorName")
        favorite_id = find(key="favoriteId")
        favorite_group = find(key="favoriteGroup")
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
    import pprint

    cache_path = Path("./cache/")
    last_cache_file: Path = max(cache_path.glob("*"), key=lambda path: path.stat().st_mtime)
    fetched_dict_list = orjson.loads(last_cache_file.read_bytes())
    for entry in fetched_dict_list[:3]:
        fetched_info = FetchedInfo.create(entry)
        pprint.pprint(fetched_info)
