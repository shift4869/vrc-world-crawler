import time
from logging import INFO, getLogger
from pathlib import Path

from vrc_world_crawler.crawler.fetcher import Fetcher
from vrc_world_crawler.crawler.valueobject.fetched_info import FetchedInfo
from vrc_world_crawler.db.favorite_world_db import FavoriteWorldDB
from vrc_world_crawler.db.model import FavoriteWorld

logger = getLogger(__name__)
logger.setLevel(INFO)


class Crawler:
    config_path: Path = Path("./config/config.json")
    fetcher: Fetcher
    db: FavoriteWorldDB

    def __init__(self) -> None:
        logger.info("Crawler init -> start")
        self.fetcher = Fetcher(self.config_path, is_debug=False)
        self.db = FavoriteWorldDB()
        logger.info("Crawler init -> done")

    def run(self) -> None:
        logger.info("Crawler run -> start")
        fetched_info_list: list[FetchedInfo] = self.fetcher.fetch()

        if not fetched_info_list:
            logger.info("fetched_info_list is empty.")
            return

        logger.info("DB control -> start.")
        self.db.clear_favorited()
        record_list = [FavoriteWorld.create(fetched_info.to_dict()) for fetched_info in fetched_info_list]
        self.db.upsert(record_list)
        logger.info("DB control -> done.")

        logger.info("Crawler run -> done")


if __name__ == "__main__":
    import logging.config
    from logging import getLogger

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    logger = getLogger(__name__)
    crawler = Crawler()
    crawler.run()
