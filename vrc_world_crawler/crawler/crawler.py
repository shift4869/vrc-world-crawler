import time
from logging import INFO, getLogger
from pathlib import Path

logger = getLogger(__name__)
logger.setLevel(INFO)


class Crawler:
    config_path: Path = Path("./config/config.json")

    def __init__(self) -> None:
        logger.info("Crawler init -> start")
        logger.info("Crawler init -> done")

    def run(self) -> None:
        logger.info("Crawler run -> start")

        logger.info("DB control -> start.")
        logger.info("DB control -> done.")

        logger.info("Crawler run -> done")


if __name__ == "__main__":
    import logging.config
    from logging import getLogger

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    logger = getLogger(__name__)
    crawler = Crawler()
    crawler.run()
