from collections import defaultdict
from logging import INFO, getLogger
from pathlib import Path

import orjson

from vrc_world_crawler.db.favorite_world_db import FavoriteWorldDB

logger = getLogger(__name__)
logger.setLevel(INFO)


def make_pls_json() -> None:
    """DBからPortalLibrarySystem用のjsonファイルを作成する"""
    # 入力はDB
    db = FavoriteWorldDB()
    records = db.select()

    # 出力はjson
    output_file = "./PortalLibrarySystem.json"

    # TagごとにWorldを格納
    categories = defaultdict(list)
    seen_ids = defaultdict(set)

    for record in records:
        world = {"ID": record.world_id, "Name": record.world_name, "Description": record.description}
        if record.favorite_group == "手動登録":
            categories["手動登録"].append(world)
            continue
        if not record.tags:
            categories["tag_nothing"].append(world)
            continue
        tags = record.tags.split("|")

        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue
            if world["ID"] not in seen_ids[tag]:
                categories[tag].append(world)
                seen_ids[tag].add(world["ID"])

    # TODO::ワールド名で分類

    # JSON形式に変換
    categories_result = []
    for tag, worlds in categories.items():
        categories_result.append({"Category": tag, "Worlds": worlds})
    categories_result.sort(key=lambda x: x["Category"])
    result = {"ReverseCategorys": True, "ShowPrivateWorld": True, "Categorys": categories_result}

    Path(output_file).write_bytes(orjson.dumps(result, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))

    print(f"出力完了: {output_file}")


if __name__ == "__main__":
    make_pls_json()
