import sys
import unittest
from collections import namedtuple

from mock import MagicMock, call, patch
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from vrc_world_crawler.db.favorite_world_db import FavoriteWorldDB
from vrc_world_crawler.db.model import FavoriteWorld


class TestFavoriteWorldDB(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def _get_args_dict(self) -> list:
        return {
            "world_id": "wrld_world_id",
            "world_name": "world_name",
            "world_url": "world_url",
            "description": "description",
            "author_id": "author_id",
            "author_name": "author_name",
            "favorite_id": "favorite_id",
            "favorite_group": "favorite_group",
            "is_favorited": True,
            "release_status": "public",
            "featured": 0,
            "image_url": "image_url",
            "thmbnail_image_url": "thmbnail_image_url",
            "version": 1,
            "star": 0,
            "visit": 0,
            "published_at": "2024-09-03T12:34:56.789000",
            "lab_published_at": "2024-09-02T12:34:56.789000",
            "created_at": "2024-09-01T12:34:56.789000",
            "updated_at": "2024-09-04T12:34:56.789000",
            "registered_at": "2024-09-05T12:34:56.789000",
        }

    def _get_instance(self) -> FavoriteWorldDB:
        mock_create_engine = self.enterContext(patch("vrc_world_crawler.db.base.create_engine"))
        mock_static_pool = self.enterContext(patch("vrc_world_crawler.db.base.StaticPool"))
        mock_model_base = self.enterContext(patch("vrc_world_crawler.db.base.ModelBase"))
        instance = FavoriteWorldDB("./tests/test.db")
        return instance

    def test_init(self) -> None:
        instance = self._get_instance()
        db_path = "./tests/test.db"
        db_url = f"sqlite:///{db_path}"
        self.assertEqual(db_path, instance.db_path)
        self.assertEqual(db_url, instance.db_url)

    def test_select(self) -> None:
        mock_sessionmaker = self.enterContext(patch("vrc_world_crawler.db.favorite_world_db.sessionmaker"))
        instance = self._get_instance()

        expect = mock_sessionmaker.return_value.return_value.query.return_value.all.return_value
        actual = instance.select()
        self.assertEqual(
            [
                call(bind=instance.engine, autoflush=False),
                call()(),
                call()().query(FavoriteWorld),
                call()().query().all(),
                call()().close(),
            ],
            mock_sessionmaker.mock_calls,
        )
        self.assertEqual(expect, actual)

    def test_clear_favorited(self) -> None:
        mock_sessionmaker = self.enterContext(patch("vrc_world_crawler.db.favorite_world_db.sessionmaker"))
        instance = self._get_instance()

        expect = 0
        actual = instance.clear_favorited()
        self.assertEqual(
            [
                call(bind=instance.engine, autoflush=False),
                call()(),
                call()().query(FavoriteWorld),
                call()().query().update({FavoriteWorld.is_favorited: False}),
                call()().commit(),
                call()().close(),
            ],
            mock_sessionmaker.mock_calls,
        )
        self.assertEqual(expect, actual)

    def test_upsert(self) -> None:
        mock_sessionmaker = self.enterContext(patch("vrc_world_crawler.db.favorite_world_db.sessionmaker"))
        mock_and = self.enterContext(patch("vrc_world_crawler.db.favorite_world_db.and_"))
        instance = self._get_instance()

        Params = namedtuple(
            "Params",
            [
                "is_error_occur",
                "is_args_list",
                "release_status",
                "is_insert",
                "result",
                "msg",
            ],
        )

        def pre_run(params: Params) -> FavoriteWorld | list[FavoriteWorld] | str:
            record = None
            if params.is_error_occur:
                record = "invalid args"
                return record
            else:
                record = FavoriteWorld.create(self._get_args_dict())

            record.release_status = params.release_status
            if params.is_args_list:
                record = [record]

            mock_sessionmaker.reset_mock(side_effect=True)
            mock_and.reset_mock()
            mock_session: MagicMock = mock_sessionmaker.return_value.return_value
            if params.is_insert:
                mock_session.query.return_value.filter.return_value.with_for_update.side_effect = NoResultFound
            else:
                mock_session.query.return_value.filter.return_value.with_for_update.side_effect = lambda: MagicMock()

            return record

        def post_run(params: Params, record: FavoriteWorld | list[FavoriteWorld], actual: list[int]) -> None:
            self.assertEqual(params.result, actual)

            if isinstance(record, list):
                record = record[0]

            expect_call = [
                call(bind=instance.engine, autoflush=False),
                call()(),
            ]

            if params.release_status == "public":
                if params.is_insert:
                    expect_call.extend([
                        call()().query(FavoriteWorld),
                        call()().query().filter(mock_and(FavoriteWorld.world_id == record.world_id)),
                        call()().query().filter().with_for_update(),
                        call()().add(record),
                    ])
                else:
                    expect_call.extend([
                        call()().query(FavoriteWorld),
                        call()().query().filter(mock_and(FavoriteWorld.world_id == record.world_id)),
                        call()().query().filter().with_for_update(),
                    ])
            else:
                if params.is_insert:
                    expect_call.extend([
                        call()().query(FavoriteWorld),
                        call()().query().filter(mock_and(FavoriteWorld.favorite_id == record.favorite_id)),
                        call()().query().filter().with_for_update(),
                    ])
                else:
                    expect_call.extend([
                        call()().query(FavoriteWorld),
                        call()().query().filter(mock_and(FavoriteWorld.favorite_id == record.favorite_id)),
                        call()().query().filter().with_for_update(),
                    ])

            expect_call.extend([
                call()().commit(),
                call()().close(),
            ])
            # print(expect_call)
            # print(mock_sessionmaker.mock_calls)
            self.assertEqual(
                expect_call,
                mock_sessionmaker.mock_calls,
            )

        params_list: list[Params] = [
            Params(False, False, "public", True, [0], "one public record insert"),
            Params(False, False, "public", False, [1], "one public record update"),
            Params(False, False, "private", True, [0], "one private record insert"),
            Params(False, False, "private", False, [1], "one private record update"),
            Params(False, True, "public", True, [0], "public record list insert"),
            Params(False, True, "public", False, [1], "one public record update"),
            Params(True, False, "public", True, TypeError, "invalid record"),
        ]
        for params in params_list:
            with self.subTest(params.msg):
                record = pre_run(params)
                if isinstance(params.result, list):
                    actual = instance.upsert(record)
                    post_run(params, record, actual)
                else:
                    with self.assertRaises(params.result):
                        actual = instance.upsert(record)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
