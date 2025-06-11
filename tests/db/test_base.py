import sys
import unittest

from mock import MagicMock, patch

from vrc_world_crawler.db.base import Base


class ConcreteDB(Base):
    def __init__(self, db_path: str = "./tests/test.db"):
        super().__init__(db_path)

    def select(self):
        return ["select"]

    def upsert(self, record):
        return ["upsert"]


class TestBase(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_init(self):
        mock_create_engine = self.enterContext(patch("vrc_world_crawler.db.base.create_engine"))
        mock_static_pool = self.enterContext(patch("vrc_world_crawler.db.base.StaticPool"))
        mock_model_base = self.enterContext(patch("vrc_world_crawler.db.base.ModelBase"))
        instance = ConcreteDB()

        db_path = "./tests/test.db"
        db_url = f"sqlite:///{db_path}"
        self.assertEqual(db_path, instance.db_path)
        self.assertEqual(db_url, instance.db_url)
        self.assertEqual(mock_create_engine.return_value, instance.engine)
        self.assertEqual(["select"], instance.select())
        self.assertEqual(["upsert"], instance.upsert([]))

        mock_create_engine.assert_called_once_with(
            db_url,
            echo=False,
            poolclass=mock_static_pool,
            connect_args={
                "timeout": 30,
                "check_same_thread": False,
            },
        )
        mock_create_all: MagicMock = mock_model_base.metadata.create_all
        mock_create_all.assert_called_once_with(mock_create_engine.return_value)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
