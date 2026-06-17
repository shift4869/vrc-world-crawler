from abc import ABC, abstractmethod
from datetime import datetime
from logging import INFO, getLogger
from pathlib import Path

import httpx
import orjson

from vrc_world_crawler.crawler.valueobject.fetched_info import FetchedInfo
from vrc_world_crawler.crawler.valueobject.world_url import WorldUrl

logger = getLogger(__name__)
logger.setLevel(INFO)


class FetcherBase(ABC):
    is_debug: bool
    config_dict = {}
    cache_path = Path("./cache/")

    def __init__(self, config_path: Path, is_debug: bool = False) -> None:
        logger.info("Fetcher init -> start")
        self.is_debug = is_debug
        self.config_dict = orjson.loads(config_path.read_bytes())
        self.cache_path.mkdir(parents=True, exist_ok=True)
        logger.info("Fetcher init -> done")

    def _get_client(self) -> httpx.Client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Content-Type": "application/json",
        }
        payload = {
            "apiKey": self.config_dict["vrc"]["apiKey"],
            "auth": self.config_dict["vrc"]["auth"],
            "twoFactorAuth": self.config_dict["vrc"]["twoFactorAuth"],
        }
        cookies = httpx.Cookies(payload)
        transport = httpx.HTTPTransport(retries=3)
        return httpx.Client(headers=headers, cookies=cookies, follow_redirects=True, transport=transport)

    @abstractmethod
    def _get_target(self) -> list[WorldUrl]:
        raise NotImplementedError

    @abstractmethod
    def _fetch(self, target: list[WorldUrl]) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def _create_fetched_info(self, fetched_dict_list: list[dict]) -> list[FetchedInfo]:
        raise NotImplementedError

    def fetch(self) -> list[FetchedInfo]:
        logger.info("Fetcher fetch -> start")
        logger.info("Fetching -> start")
        fetched_info_list = []
        fetched_dict_list = []
        if self.is_debug:
            last_cache_file: Path = max(self.cache_path.glob("*"), key=lambda path: path.stat().st_mtime)
            fetched_dict_list = orjson.loads(last_cache_file.read_bytes())
        else:
            target_url_list = self._get_target()
            fetched_dict_list = self._fetch(target_url_list)
            cache_filename = "favorites_world_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
            (self.cache_path / cache_filename).write_bytes(orjson.dumps(fetched_dict_list, option=orjson.OPT_INDENT_2))
        logger.info("Fetching -> done")

        logger.info("Create FetchedInfo -> start")
        fetched_info_list = self._create_fetched_info(fetched_dict_list)
        logger.info("Create FetchedInfo -> done")
        logger.info("Fetcher fetch -> done")
        return fetched_info_list


if __name__ == "__main__":
    pass
