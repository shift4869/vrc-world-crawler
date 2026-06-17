import re
from dataclasses import dataclass
from typing import Self

from vrc_world_crawler.crawler.valueobject.world_id import WorldId


@dataclass(frozen=True)
class WorldUrl:
    WORLD_URL_PATTERN1 = r"https://vrchat.com/home/world/wrld_(.*?)/info"
    WORLD_URL_PATTERN2 = r"https://vrchat.com/home/world/wrld_(.*)"
    world_url: str

    def __post_init__(self) -> None:
        """引数チェック
        Raises: ValueError
        """
        if not isinstance(self.world_url, str):
            raise ValueError("world_url must be str.")

        # フォーマットチェック
        if not (
            re.search(WorldUrl.WORLD_URL_PATTERN1, self.world_url)
            or re.search(WorldUrl.WORLD_URL_PATTERN2, self.world_url)
        ):
            raise ValueError(f"world_url must be '{WorldUrl.WORLD_URL_PATTERN1}'.")
        if re.search(WorldUrl.WORLD_URL_PATTERN1, self.world_url):
            object.__setattr__(self, "world_url", self.world_url.replace("/info", ""))  # '/info' を削除

    def to_id(self) -> WorldId:
        m = re.match(WorldUrl.WORLD_URL_PATTERN2, self.world_url)
        return WorldId("wrld_" + m.group(1)) if m else WorldId("???")

    def __str__(self) -> str:
        return self.world_url

    def to_str(self) -> str:
        return self.world_url

    @classmethod
    def create(cls, world_id_or_url: str | WorldId | Self) -> Self | ValueError:
        """WorldUrl インスタンスを作成する

        Args:
            world_id_or_url (str | WorldId): world_url or world_id を表す文字列 or WorldId型

        Returns:
            Self: WorldUrl インスタンス
        """
        if isinstance(world_id_or_url, WorldUrl):
            return WorldUrl(str(world_id_or_url))
        if isinstance(world_id_or_url, WorldId):
            return WorldUrl(WorldUrl.WORLD_URL_PATTERN2.replace("(.*)", "") + str(world_id_or_url))
        elif isinstance(world_id_or_url, str):
            if re.search(WorldUrl.WORLD_URL_PATTERN1, world_id_or_url) or re.search(
                WorldUrl.WORLD_URL_PATTERN2, world_id_or_url
            ):
                return WorldUrl(world_id_or_url)
            else:
                return WorldUrl(WorldUrl.WORLD_URL_PATTERN2.replace("(.*)", "") + world_id_or_url)
        raise ValueError


if __name__ == "__main__":
    url1 = "https://vrchat.com/home/world/wrld_fb2d8457-c02e-400b-aeb1-dde094f0f912/info"
    url2 = "https://vrchat.com/home/world/wrld_fb2d8457-c02e-400b-aeb1-dde094f0f912"
    world_url = WorldUrl(url1)
    world_url = WorldUrl(url2)
    print(world_url)
    world_id = world_url.to_id()
    print(world_id)
    world_url = WorldUrl.create(url1)
    world_url = WorldUrl.create(world_id)
    world_url = WorldUrl.create(str(world_id))
