import csv
import functools
import random
import re
import time
from datetime import datetime
from logging import INFO, getLogger
from pathlib import Path

import httpx
import orjson

from vrc_world_crawler.crawler.valueobject.fetched_info import FetchedInfo
from vrc_world_crawler.db.favorite_world_db import FavoriteWorldDB
from vrc_world_crawler.db.model import FavoriteWorld
from vrc_world_crawler.util import find_values, normalize_date_at, tags_join

logger = getLogger(__name__)
logger.setLevel(INFO)

VRC_WORLD_URL_PATTERN = "https://vrchat.com/home/world/wrld_(.*?)/info"
BASE_UEL = "https://vrchat.com/api/1/worlds/{}?includeInstances=partial"


def register(url: str) -> None:
    if not url or url == "":
        return
    m = re.match(VRC_WORLD_URL_PATTERN, url)
    if not m:
        return
    logger.info(f"Target world url is '{url}'.")
    world_id = "wrld_" + m.group(1)
    fetch_url = BASE_UEL.format(world_id)

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

    db = FavoriteWorldDB()
    records = db.select()
    record = [r for r in records if r.world_url in url][0]
    response_dict |= {"favoriteId": record.favorite_id}
    response_dict |= {"favoriteGroup": record.favorite_group}

    record = FavoriteWorld.create(FetchedInfo.create(response_dict).to_dict())
    db.upsert(record)
    return


def manual_all_update() -> None:
    """現在お気に入りに入っていないワールドについて情報を再取得する"""
    url_list = []
    input_file_path = "./FavoriteWorld.csv"

    with open(input_file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # if row["is_favorited"] == "0":
            if row["tags"] == "":
                url = f"https://vrchat.com/home/world/{row['world_id']}/info"
                url_list.append(url)

    error_num = 0
    n = len(url_list)
    for i, url in enumerate(url_list):
        try:
            wait_time = random.uniform(0.5, 1)
            register(url)
            time.sleep(wait_time)
            print(f"{i}/{n} fetching ...")
        except Exception:
            error_num += 1
    if error_num:
        print(f"occur {error_num} errors.")


if __name__ == "__main__":
    manual_all_update()
