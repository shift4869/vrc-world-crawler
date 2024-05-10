import pprint
from datetime import datetime
from logging import INFO, getLogger
from pathlib import Path

import orjson

from vrc_world_crawler.crawler.valueobject.fetched_info import FetchedInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class Fetcher:
    is_debug: bool
    cache_path = Path("./cache/")

    def __init__(self, config_path: Path, is_debug: bool = False) -> None:
        logger.info("Fetcher init -> start")
        config_dict = orjson.loads(config_path.read_bytes())
        self.cache_path.mkdir(parents=True, exist_ok=True)
        logger.info("Fetcher init -> done")

    def fetch(self) -> list[FetchedInfo]:
        logger.info("Fetcher fetch -> start")
        fetched_info_list = []
        logger.info("Create FetchedInfo -> start")
        logger.info("Create FetchedInfo -> done")
        logger.info("Fetcher fetch -> done")
        return fetched_info_list


if __name__ == "__main__":
    import logging.config

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    config_path: Path = Path("./config/config.json")
    cache_path = Path("./cache/")

    fetcher = Fetcher(config_path, is_debug=True)
    response = fetcher.fetch()
    pprint.pprint(response)
