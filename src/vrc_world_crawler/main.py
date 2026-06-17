import argparse
import logging.config
from logging import INFO, getLogger

from vrc_world_crawler.crawler.crawler import Crawler
from vrc_world_crawler.manual_register import manual_register

logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
# for name in logging.root.manager.loggerDict:
#     if "vrc_world_crawler" not in name:
#         getLogger(name).disabled = True
logger = getLogger(__name__)
logger.setLevel(INFO)


def main() -> None:
    horizontal_line = "-" * 80
    logger.info(horizontal_line)
    logger.info("VRC world crawler -> start")

    # 引数受付
    parser = argparse.ArgumentParser(description="mode select")
    parser.add_argument("--mode", help="running mode [auto/manual]", default="auto")
    parser.add_argument("--url", help="url for manual register {type string}", default="")
    args = parser.parse_args()

    if args.mode == "auto":
        logger.info("Running mode is auto.")
        crawler = Crawler()
        crawler.run()
    elif args.mode == "manual":
        logger.info("Running mode is manual.")
        url = args.url
        if isinstance(url, str):
            url = [url]
        manual_register(url)
    else:
        logger.wa("Running mode is invalid.")

    logger.info("VRC world crawler -> done")
    logger.info(horizontal_line)


if __name__ == "__main__":
    main()
