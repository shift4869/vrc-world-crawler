import pprint
from datetime import datetime
from logging import INFO, getLogger
from pathlib import Path

import httpx
import orjson

from vrc_world_crawler.crawler.valueobject.fetched_info import FetchedInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class Fetcher:
    is_debug: bool
    cache_path = Path("./cache/")
    cookie_dict: dict

    def __init__(self, config_path: Path, is_debug: bool = False) -> None:
        logger.info("Fetcher init -> start")
        self.config_dict = orjson.loads(config_path.read_bytes())
        self.is_debug = is_debug
        self.cache_path.mkdir(parents=True, exist_ok=True)
        logger.info("Fetcher init -> done")

    def fetch(self) -> list[FetchedInfo]:
        logger.info("Fetcher fetch -> start")
        logger.info("Fetching -> start")
        fetched_info_list = []
        fetched_dict_list = []
        if self.is_debug:
            last_cache_file: Path = max(self.cache_path.glob("*"), key=lambda path: path.stat().st_mtime)
            fetched_dict_list = orjson.loads(last_cache_file.read_bytes())
        else:
            response = None
            response_list = []
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
            base_url = "https://vrchat.com/api/1/worlds/favorites?n=50&offset={}&tag=worlds{}"
            with httpx.Client(follow_redirects=True, transport=transport) as client:
                for world_index in [1, 2, 3, 4]:
                    for offset_count in [0, 50, 100, 150, 200, 250, 300]:
                        url = base_url.format(offset_count, world_index)

                        response = client.get(url, headers=headers, cookies=cookies)
                        response.raise_for_status()
                        if not response.text:
                            break
                        response_dict = orjson.loads(response.text)
                        if not response_dict:
                            break
                        response_list.append(response_dict)

            base_url = "https://vrchat.com/api/1/worlds/favorites?n=50&offset={}&tag=vrcPlusWorlds{}"
            with httpx.Client(follow_redirects=True, transport=transport) as client:
                for world_index in [1, 2, 3, 4]:
                    for offset_count in [0, 50, 100, 150, 200, 250, 300]:
                        url = base_url.format(offset_count, world_index)

                        response = client.get(url, headers=headers, cookies=cookies)
                        response.raise_for_status()
                        if not response.text:
                            break
                        response_dict = orjson.loads(response.text)
                        if not response_dict:
                            break
                        response_list.append(response_dict)

            if not response_list:
                logger.info("Fetching -> failed")
                raise ValueError("Fetching failed, null response.")

            for response_dict_list in response_list:
                fetched_dict_list.extend(response_dict_list)  # flatten
            cache_filename = "favorites_world_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
            (self.cache_path / cache_filename).write_bytes(orjson.dumps(fetched_dict_list, option=orjson.OPT_INDENT_2))
        logger.info("Fetching -> done")

        logger.info("Create FetchedInfo -> start")
        for fetched_dict in fetched_dict_list:
            try:
                fetched_info_list.append(FetchedInfo.create(fetched_dict))
            except Exception:
                pass
        logger.info("Create FetchedInfo -> done")
        logger.info("Fetcher fetch -> done")
        return fetched_info_list


if __name__ == "__main__":
    import logging.config

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    config_path: Path = Path("./config/config.json")
    cache_path = Path("./cache/")

    fetcher = Fetcher(config_path, is_debug=False)
    response = fetcher.fetch()
    pprint.pprint(response)
