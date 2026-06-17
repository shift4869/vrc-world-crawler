import csv
import logging.config
from logging import INFO, getLogger

from vrc_world_crawler.manual_register import manual_register

logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
# for name in logging.root.manager.loggerDict:
#     if "vrc_world_crawler" not in name:
#         getLogger(name).disabled = True
logger = getLogger(__name__)
logger.setLevel(INFO)


def manual_csv_register() -> None:
    url_list = []
    input_file_path = "./FavoriteWorld.csv"

    with open(input_file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # if row["is_favorited"] == "0":
            if not row["tags"]:
                url = f"https://vrchat.com/home/world/{row['world_id']}/info"
                url_list.append(url)

    manual_register(url_list)


if __name__ == "__main__":
    manual_csv_register()
