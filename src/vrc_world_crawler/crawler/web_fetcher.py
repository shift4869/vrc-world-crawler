import pprint
from logging import INFO, getLogger
from pathlib import Path

import orjson

from vrc_world_crawler.crawler.fetcher_base import FetcherBase
from vrc_world_crawler.crawler.valueobject.fetched_info import FetchedInfo
from vrc_world_crawler.crawler.valueobject.world_url import WorldUrl
from vrc_world_crawler.db.favorite_world_db import FavoriteWorldDB

logger = getLogger(__name__)
logger.setLevel(INFO)


class WebFetcher(FetcherBase):
    def __init__(self, config_path: Path, is_debug: bool = False) -> None:
        super().__init__(config_path, is_debug)

    def _get_target(self) -> list[WorldUrl]:
        # Webから取得するため、この時点では対象のWorldUrlは未確定
        # よって空の配列を返す
        return []

    def _fetch(self, target: list[WorldUrl]) -> list[dict]:
        fetched_dict_list: list[dict] = []
        response = None
        response_list: list[dict] = []
        response_dict_list_flatten: list[dict] = []
        self.client = self._get_client()
        base_url = "https://vrchat.com/api/1/worlds/favorites?n=50&offset={}&tag=worlds{}"
        for world_index in [1, 2, 3, 4]:
            for offset_count in [0, 50, 100, 150, 200, 250, 300]:
                url = base_url.format(offset_count, world_index)

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
                response_list.append(response_dict)

        base_url = "https://vrchat.com/api/1/worlds/favorites?n=50&offset={}&tag=vrcPlusWorlds{}"
        for world_index in [1, 2, 3, 4]:
            for offset_count in [0, 50, 100, 150, 200, 250, 300]:
                url = base_url.format(offset_count, world_index)

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
                response_list.append(response_dict)
        self.client.close()

        if not response_list:
            logger.info("Fetching -> failed")
            raise ValueError("Fetching failed, null response.")

        for response_dict_list in response_list:
            response_dict_list_flatten.extend(response_dict_list)  # flatten

        for response_dict in response_dict_list_flatten:
            fetched_dict_list.append(response_dict | {"isFavorited": True})
        return fetched_dict_list

    def _create_fetched_info(self, fetched_dict_list: list[dict]) -> list[FetchedInfo]:
        fetched_info_list: list[FetchedInfo] = []
        for fetched_dict in fetched_dict_list:
            try:
                fetched_info_list.append(FetchedInfo.create(fetched_dict))
            except Exception:
                pass
        return fetched_info_list


if __name__ == "__main__":
    import logging.config

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    config_path: Path = Path("./config/config.json")
    cache_path = Path("./cache/")

    fetcher = WebFetcher(config_path, is_debug=False)
    response = fetcher.fetch()
    pprint.pprint(response)
