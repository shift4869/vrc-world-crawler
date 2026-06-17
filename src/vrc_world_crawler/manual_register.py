from logging import INFO, getLogger
from pathlib import Path

from vrc_world_crawler.crawler.manual_fetcher import ManualFetcher
from vrc_world_crawler.db.favorite_world_db import FavoriteWorldDB
from vrc_world_crawler.db.model import FavoriteWorld

logger = getLogger(__name__)
logger.setLevel(INFO)


def manual_register(url_list: list[str]) -> None:
    config_path: Path = Path("./config/config.json")
    fetcher = ManualFetcher(url_list, config_path, is_debug=False)
    fetched_info_list = fetcher.fetch()
    record_list = [FavoriteWorld.create(fetched_info.to_dict()) for fetched_info in fetched_info_list]

    db: FavoriteWorldDB = FavoriteWorldDB()
    db.upsert(record_list)


if __name__ == "__main__":
    url_list = [
        # "https://vrchat.com/home/world/wrld_f612c90d-1a12-4355-8683-215c3a34c8ed/info",  # public
        # "https://vrchat.com/home/world/wrld_fb2d8457-c02e-400b-aeb1-dde094f0f912/info",  # private
        # "https://vrchat.com/home/world/wrld_8d534a31-7080-4284-9cae-cfa5a4da2170/info",  # private
        "https://vrchat.com/home/world/wrld_7edc99f7-653f-4939-8d2e-30c72c69e8e9/info",
    ]
    manual_register(url_list)
