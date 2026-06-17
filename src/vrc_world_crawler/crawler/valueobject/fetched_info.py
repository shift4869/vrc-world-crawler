import functools
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Self

import orjson

from vrc_world_crawler.crawler.valueobject.world_id import WorldId
from vrc_world_crawler.crawler.valueobject.world_url import WorldUrl
from vrc_world_crawler.db.favorite_world_db import FavoriteWorldDB
from vrc_world_crawler.util import find_values, normalize_date_at, tags_join


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
    is_favorited: bool
    release_status: str
    featured: int
    image_url: str
    thumbnail_image_url: str
    version: int
    star: int
    visit: int
    tags: str
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
            raise ValueError("world_name must be str")
        if not isinstance(self.world_url, str):
            raise ValueError("world_url must be str")
        if not isinstance(self.description, str):
            raise ValueError("description must be str")
        if not isinstance(self.author_id, str):
            raise ValueError("author_id must be str")
        if not isinstance(self.author_name, str):
            raise ValueError("author_name must be str")
        if not isinstance(self.favorite_id, str):
            raise ValueError("favorite_id must be str")
        if not isinstance(self.favorite_group, str):
            raise ValueError("favorite_group must be str")
        if not isinstance(self.is_favorited, bool):
            raise ValueError("is_favorited must be bool")
        if not isinstance(self.release_status, str):
            raise ValueError("release_status must be str")
        if not isinstance(self.featured, int):
            raise ValueError("featured must be int")
        if not isinstance(self.image_url, str):
            raise ValueError("image_url must be str")
        if not isinstance(self.thumbnail_image_url, str):
            raise ValueError("thumbnail_image_url must be str")
        if not isinstance(self.version, int):
            raise ValueError("version must be int")
        if not isinstance(self.star, int):
            raise ValueError("star must be int")
        if not isinstance(self.visit, int):
            raise ValueError("visit must be int")
        if not isinstance(self.tags, str):
            raise ValueError("tags must be str")
        if not isinstance(self.published_at, str):
            raise ValueError("published_at must be str")
        if not isinstance(self.lab_published_at, str):
            raise ValueError("lab_published_at must be str")
        if not isinstance(self.created_at, str):
            raise ValueError("created_at must be str")
        if not isinstance(self.updated_at, str):
            raise ValueError("updated_at must be str")
        if not isinstance(self.registered_at, str):
            raise ValueError("registered_at must be str")

        # world_id フォーマットチェック
        if not (re.search(WorldId.WORLD_ID_PATTERN, self.world_id) or self.world_id == "???"):
            raise ValueError("world_id must be 'wrld_.*' or '???'.")

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
            "is_favorited": self.is_favorited,
            "release_status": self.release_status,
            "featured": self.featured,
            "image_url": self.image_url,
            "thumbnail_image_url": self.thumbnail_image_url,
            "version": self.version,
            "star": self.star,
            "visit": self.visit,
            "tags": self.tags,
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
        値について、上から優先とする
            (1)fetched_dict で渡された辞書について、キーが完全ならば fetched_dict の値を使う
            (2)既にDBに格納済の場合、DBに格納されている値を使う
            (3)DBに格納されていない場合、不完全な fetched_dict にあればそれを使う
            (4)各項目のデフォルト値
        ただし fetched_dict はキーとして "id" または "worldId" または "worldUrl" の最低でもどれか一つを持つ必要がある

        このメソッドでは上記の優先度を加味した値の設定を行う
        各項目の型チェックは __post_init__ で行う

        Args:
            fetched_dict (dict): fetch したデータ辞書の1レコードを想定した辞書
                キーとして "id" または  "worldId" または "worldUrl" の最低でもどれか一つを持つ必要がある

        Returns:
            Self: FetchedInfo インスタンス
        """
        # 入力チェック
        required_keys = ["id", "worldId", "worldUrl"]
        if not bool(set(fetched_dict.keys()) & set(required_keys)):
            # 必須のキーを一つも含んでいない
            raise ValueError("fetched_dict key error.")

        # world_id と world_url セット
        world_id = ""
        world_url = ""
        if "id" in fetched_dict:
            world_id = WorldId.create(fetched_dict["id"]).to_str()
            world_url = WorldUrl.create(world_id).to_str() if world_id != "???" else "???"
        elif "worldId" in fetched_dict:
            world_id = WorldId.create(fetched_dict["worldId"]).to_str()
            world_url = WorldUrl.create(world_id).to_str() if world_id != "???" else "???"
        else:  # "worldUrl" in fetched_dict:
            world_url = WorldUrl.create(fetched_dict["worldUrl"])
            world_id = world_url.to_id().to_str()
            world_url = world_url.to_str()
        if world_id == "" or world_url == "":
            # 必須のキーを一つも含んでいない
            raise ValueError("fetched_dict key error.")
        fetched_dict |= {"worldId": world_id}
        fetched_dict |= {"worldUrl": world_url}

        registered_at = datetime.now().isoformat()
        default_dict = {
            "worldId": "???",
            "name": "???",
            "worldUrl": "???",
            "description": "",
            "authorId": "???",
            "authorName": "???",
            "favoriteId": "???",
            "favoriteGroup": "???",
            "isFavorited": False,
            "releaseStatus": "private",
            "featured": 0,
            "imageUrl": "",
            "thumbnailImageUrl": "",
            "version": 0,
            "favorites": 0,
            "visits": 0,
            "tags": "",
            "publicationDate": "",
            "labsPublicationDate": "",
            "created_at": registered_at,
            "updated_at": registered_at,
        }
        perfect_keys = list(default_dict.keys())
        is_input_key_is_perfect = len(set(fetched_dict.keys()) & set(perfect_keys)) == len(perfect_keys)

        db: FavoriteWorldDB = None
        if not is_input_key_is_perfect:
            db = FavoriteWorldDB()

        record_dict = {}
        if db:
            r = db.select_from_world_id(world_id)
            if (not r) and ("favoriteId" in fetched_dict):
                r = db.select_from_favorite_id(fetched_dict["favoriteId"])
            if r:
                for key, value in zip(perfect_keys, r.to_dict().values()):
                    record_dict[key] = value
                fetched_dict = {}
                world_id = record_dict["worldId"]
                world_url = record_dict["worldUrl"]

        registered_at = datetime.now().isoformat()
        # find = functools.partial(find_values, obj=fetched_dict, is_predict_one=True, key_white_list=[""])

        # fetch データの辞書解析
        # release_status = find(key="releaseStatus")
        # if release_status != "public":
        #     # release_status が "public" でない場合
        #     # 現在公開されていないワールドの可能性が高い
        #     # 取得できる情報のみ取得する
        #     # ただし world_id, world_name, author_name は "???" となっているため実質的に情報を持たない
        #     # favorite_id は有効なのでこれで紐づける
        #     world_id = find(key="id")
        #     world_name = find(key="name")
        #     author_name = find(key="authorName")
        #     favorite_id = find(key="favoriteId")
        #     favorite_group = find(key="favoriteGroup")
        #     tags = tags_join(find(key="tags"))
        #     is_favorited = True
        #     return FetchedInfo(
        #         world_id,
        #         world_name,
        #         "",
        #         "",
        #         "",
        #         author_name,
        #         favorite_id,
        #         favorite_group,
        #         is_favorited,
        #         release_status,
        #         -1,
        #         "",
        #         "",
        #         -1,
        #         -1,
        #         -1,
        #         tags,
        #         "",
        #         "",
        #         "",
        #         "",
        #         registered_at,
        #     )
        def find(key: str) -> Any:
            if key in fetched_dict:
                return fetched_dict[key]
            if key in record_dict:
                return record_dict[key]
            if key in default_dict:
                return default_dict[key]
            raise ValueError(f"not found key error: {key}")

        world_name = find(key="name")
        description = find(key="description")
        author_id = find(key="authorId")
        author_name = find(key="authorName")
        favorite_id = find(key="favoriteId")
        favorite_group = find(key="favoriteGroup")
        is_favorited = find(key="isFavorited")
        release_status = find(key="releaseStatus")
        featured = 1 if bool(find(key="featured")) else 0
        image_url = find(key="imageUrl")
        thumbnail_image_url = find(key="thumbnailImageUrl")
        version = int(find(key="version"))
        star = int(find(key="favorites"))
        visit = int(find(key="visits"))
        tags = tags_join(find(key="tags"))
        published_at_str = find(key="publicationDate")
        published_at = (
            "" if published_at_str == "none" or published_at_str == "" else normalize_date_at(published_at_str)
        )
        lab_published_at_str = find(key="labsPublicationDate")
        lab_published_at = (
            ""
            if lab_published_at_str == "none" or lab_published_at_str == ""
            else normalize_date_at(lab_published_at_str)
        )
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
            is_favorited,
            release_status,
            featured,
            image_url,
            thumbnail_image_url,
            version,
            star,
            visit,
            tags,
            published_at,
            lab_published_at,
            created_at,
            updated_at,
            registered_at,
        )


if __name__ == "__main__":
    fetched_info = FetchedInfo.create({"worldId": -1})
    import pprint

    cache_path = Path("./cache/")
    last_cache_file: Path = max(cache_path.glob("*"), key=lambda path: path.stat().st_mtime)
    fetched_dict_list = orjson.loads(last_cache_file.read_bytes())
    for entry in fetched_dict_list[:3]:
        fetched_info = FetchedInfo.create(entry)
        pprint.pprint(fetched_info)
