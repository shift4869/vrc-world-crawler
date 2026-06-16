import re
from datetime import datetime
from logging import INFO, getLogger
from pathlib import Path

import httpx
import orjson

from vrc_world_crawler.db.favorite_world_db import FavoriteWorldDB
from vrc_world_crawler.db.model import FavoriteWorld
from vrc_world_crawler.util import normalize_date_at, tags_join

logger = getLogger(__name__)
logger.setLevel(INFO)

VRC_WORLD_URL_PATTERN = "https://vrchat.com/home/world/wrld_(.*?)/info"
BASE_UEL = "https://vrchat.com/api/1/worlds/{}?includeInstances=partial"


def manual_register(url: str) -> None:
    logger.info("Manual register -> start")
    if not url or url == "":
        logger.info("Manual register aborted: url is empty.")
        logger.info("Manual register -> abort")
        return
    m = re.match(VRC_WORLD_URL_PATTERN, url)
    if not m:
        logger.info("Manual register aborted: url is invalid.")
        logger.info(f"Expect pattern is '{VRC_WORLD_URL_PATTERN}'.")
        logger.info("Manual register -> abort")
        return
    logger.info(f"Target world url is '{url}'.")
    world_id = "wrld_" + m.group(1)
    fetch_url = BASE_UEL.format(world_id)

    logger.info("Fetching -> start")
    logger.info(f"Fetch url is '{fetch_url}'.")
    config_path: Path = Path("./config/config.json")
    config_dict = orjson.loads(config_path.read_bytes())
    response = None
    response_dict = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Content-Type": "application/json",
    }
    payload = {
        "apiKey": config_dict["vrc"]["apiKey"],
        "auth": config_dict["vrc"]["auth"],
        "twoFactorAuth": config_dict["vrc"]["twoFactorAuth"],
    }
    cookies = httpx.Cookies(payload)
    transport = httpx.HTTPTransport(retries=3)
    with httpx.Client(follow_redirects=True, transport=transport) as client:
        response = client.get(fetch_url, headers=headers, cookies=cookies)
        response.raise_for_status()
        response_dict = orjson.loads(response.text)
    logger.info("Fetching -> done")

    logger.info("Register -> start")
    db = FavoriteWorldDB()
    registered_at = datetime.now().isoformat()
    fetched_info = {
        "world_id": world_id,
        "world_name": response_dict["name"],
        "world_url": url,
        "description": response_dict["description"],
        "author_id": response_dict["authorId"],
        "author_name": response_dict["authorName"],
        "favorite_id": "",
        "favorite_group": "手動登録",
        "is_favorited": False,
        "release_status": response_dict["releaseStatus"],
        "featured": response_dict["featured"],
        "image_url": response_dict["imageUrl"],
        "thumbnail_image_url": response_dict["thumbnailImageUrl"],
        "version": response_dict["version"],
        "star": 0,
        "visit": response_dict["visits"],
        "tags": tags_join(response_dict["tags"]),
        "published_at": "",
        "lab_published_at": "",
        "created_at": normalize_date_at(response_dict["created_at"]),
        "updated_at": normalize_date_at(response_dict["updated_at"]),
        "registered_at": registered_at,
    }
    record_list = [FavoriteWorld.create(fetched_info)]
    db.upsert(record_list)
    logger.info("Register -> done")

    logger.info("Manual register -> done")
    return


if __name__ == "__main__":
    # url = "https://vrchat.com/home/world/wrld_fb2d8457-c02e-400b-aeb1-dde094f0f912/info"
    url = "https://vrchat.com/home/world/wrld_508f000a-34c5-4dbf-8f12-4a00669d3a90/info"
    manual_register(url)
