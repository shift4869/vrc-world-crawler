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
        """headers と cookies を設定したクライアントを返す

        アクセス時に必要なトークン類もここで設定する

        Returns:
            httpx.Client: 設定済クライアント
        """
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
        """fetch 対象のワールドURLリストを返す

        Raises:
            NotImplementedError: 派生クラスで未実装

        Returns:
            list[WorldUrl]: fetch 対象のワールドURLリスト
        """
        raise NotImplementedError

    @abstractmethod
    def _fetch(self, target: list[WorldUrl]) -> list[dict]:
        """対象のワールドURLリストをもとに実際に fetch する

        Args:
            target (list[WorldUrl]): 対象のワールドURLリスト

        Raises:
            NotImplementedError: 派生クラスで未実装

        Returns:
            list[dict]: fetch 後の返り値を格納した辞書リスト
        """
        raise NotImplementedError

    @abstractmethod
    def _create_fetched_info(self, fetched_dict_list: list[dict]) -> list[FetchedInfo]:
        """fetch 後の返り値から FetchedInfo リストを返す

        Args:
            fetched_dict_list (list[dict]): fetch 後の返り値リスト

        Raises:
            NotImplementedError: 派生クラスで未実装

        Returns:
            list[FetchedInfo]: 最終的な返り値としての FetchedInfo リスト
        """
        raise NotImplementedError

    def fetch(self) -> list[FetchedInfo]:
        """fetch の大枠の流れを定義したベース fetch メソッド

        Returns:
            list[FetchedInfo]: 最終的な返り値としての FetchedInfo リスト
        """
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
    import logging.config
    import pprint

    from vrc_world_crawler.crawler.manual_fetcher import ManualFetcher

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    config_path: Path = Path("./config/config.json")
    cache_path = Path("./cache/")

    url = [
        # "https://vrchat.com/home/world/wrld_f612c90d-1a12-4355-8683-215c3a34c8ed/info",  # public
        # "https://vrchat.com/home/world/wrld_fb2d8457-c02e-400b-aeb1-dde094f0f912/info",  # private
        # "https://vrchat.com/home/world/wrld_8d534a31-7080-4284-9cae-cfa5a4da2170/info",  # private
        "https://vrchat.com/home/world/wrld_4ef01e47-0900-43ab-ba66-ee9f9fde9349/info",
    ]
    fetcher = ManualFetcher(url, config_path, is_debug=False)
    response = fetcher.fetch()
    pprint.pprint(response)
