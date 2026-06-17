import pprint
import time
from datetime import datetime
from logging import INFO, getLogger
from pathlib import Path

import orjson

from vrc_world_crawler.crawler.fetcher_base import FetcherBase
from vrc_world_crawler.crawler.valueobject.fetched_info import FetchedInfo
from vrc_world_crawler.crawler.valueobject.world_url import WorldUrl
from vrc_world_crawler.db.favorite_world_db import FavoriteWorldDB
from vrc_world_crawler.util import normalize_date_at, tags_join

logger = getLogger(__name__)
logger.setLevel(INFO)


class ManualFetcher(FetcherBase):
    def __init__(self, target_world_url_list: list[str], config_path: Path, is_debug: bool = False) -> None:
        if not isinstance(target_world_url_list, list):
            raise ValueError
        if not all([isinstance(target_world_url, str) for target_world_url in target_world_url_list]):
            raise ValueError
        self.target_world_url_list = target_world_url_list
        super().__init__(config_path, is_debug)

    def _get_target(self) -> list[WorldUrl]:
        return [WorldUrl.create(target_world_url) for target_world_url in self.target_world_url_list]

    def _fetch(self, target: list[WorldUrl]) -> list[dict]:
        fetched_dict_list: list[dict] = []
        response = None
        self.client = self._get_client()
        base_url = "https://vrchat.com/api/1/worlds/{}?includeInstances=partial"
        n = len(target)
        for i, world_url in enumerate(target):
            url = base_url.format(world_url.to_id())

            try:
                response = self.client.get(url)
                response.raise_for_status()
            except Exception:
                continue

            if not response.text:
                break
            response_dict = orjson.loads(response.text)
            if not response_dict:
                break
            fetched_dict_list.append(response_dict | {"world_url": world_url})
            logger.info(f"{i}/{n} fetching ...")
            time.sleep(0.1)

        self.client.close()

        if not fetched_dict_list:
            logger.info("Fetching -> failed")
            raise ValueError("Fetching failed, null response.")

        return fetched_dict_list

    def _create_fetched_info(self, fetched_dict_list: list[dict]) -> list[FetchedInfo]:
        fetched_info_list: list[FetchedInfo] = []
        registered_at = datetime.now().isoformat()
        db = FavoriteWorldDB()
        for fetched_dict in fetched_dict_list:
            world_url = WorldUrl.create(fetched_dict["world_url"])
            world_id = str(world_url.to_id())
            record = db.select_from_world_id(world_id)
            fetched_info_dict = {
                "id": world_id,
                "name": fetched_dict["name"],
                "worldUrl": str(world_url),
                "description": fetched_dict["description"],
                "authorId": fetched_dict["authorId"],
                "authorName": fetched_dict["authorName"],
                "favoriteId": record.favorite_id if record else "",
                "favoriteGroup": record.favorite_group if record else "手動登録",
                "isFavorited": record.is_favorited if record else False,
                "releaseStatus": fetched_dict["releaseStatus"],
                "featured": fetched_dict["featured"],
                "imageUrl": fetched_dict["imageUrl"],
                "thumbnailImageUrl": fetched_dict["thumbnailImageUrl"],
                "version": fetched_dict["version"],
                "favorites": fetched_dict["favorites"],
                "visits": fetched_dict["visits"],
                "tags": tags_join(fetched_dict["tags"]),
                "publicationDate": record.published_at if record else "",
                "labsPublicationDate": record.lab_published_at if record else "",
                "created_at": normalize_date_at(fetched_dict["created_at"]),
                "updated_at": normalize_date_at(fetched_dict["updated_at"]),
                "registered_at": registered_at,
            }
            fetched_info = FetchedInfo.create(fetched_info_dict)
            fetched_info_list.append(fetched_info)
        return fetched_info_list


if __name__ == "__main__":
    import logging.config

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    config_path: Path = Path("./config/config.json")
    cache_path = Path("./cache/")

    url = [
        # "https://vrchat.com/home/world/wrld_f612c90d-1a12-4355-8683-215c3a34c8ed/info",  # public
        # "https://vrchat.com/home/world/wrld_fb2d8457-c02e-400b-aeb1-dde094f0f912/info",  # private
        # "https://vrchat.com/home/world/wrld_8d534a31-7080-4284-9cae-cfa5a4da2170/info",  # private
        "https://vrchat.com/home/world/wrld_7edc99f7-653f-4939-8d2e-30c72c69e8e9/info",
    ]
    fetcher = ManualFetcher(url, config_path, is_debug=False)
    response = fetcher.fetch()
    pprint.pprint(response)
