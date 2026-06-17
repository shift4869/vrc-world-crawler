import re
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class WorldId:
    WORLD_ID_PATTERN = "wrld_.*"
    world_id: str

    def __post_init__(self) -> None:
        """引数チェック
        Raises: ValueError
        """
        if not isinstance(self.world_id, str):
            raise ValueError("world_id must be str.")

        # フォーマットチェック
        if not (re.search(WorldId.WORLD_ID_PATTERN, self.world_id) or self.world_id == "???"):
            raise ValueError("world_id must be 'wrld_.*' or '???'.")

    def __str__(self) -> str:
        return self.world_id

    def to_str(self) -> str:
        return self.world_id

    @classmethod
    def create(cls, world_id: str) -> Self:
        """WorldId インスタンスを作成する

        Args:
            world_id (str): world_idを表す文字列

        Returns:
            Self: WorldId インスタンス
        """
        return WorldId(world_id)


if __name__ == "__main__":
    world_id = WorldId("wrld_fb2d8457-c02e-400b-aeb1-dde094f0f912")
    print(world_id)
