import re
import sys
import unittest
from collections import namedtuple
from datetime import datetime, timedelta

import freezegun

from vrc_world_crawler.crawler.valueobject.fetched_info import FetchedInfo


class TestFetchedInfo(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def _get_valid_args(self) -> list:
        return [
            "wrld_world_id",
            "world_name",
            "world_url",
            "description",
            "author_id",
            "author_name",
            "favorite_id",
            "favorite_group",
            True,
            "public",
            0,
            "image_url",
            "thmbnail_image_url",
            1,
            0,
            0,
            "2024-09-03T12:34:56.789000",
            "2024-09-02T12:34:56.789000",
            "2024-09-01T12:34:56.789000",
            "2024-09-04T12:34:56.789000",
            "2024-09-05T12:34:56.789000",
        ]

    def test_init(self):
        Params = namedtuple(
            "Params",
            [
                "is_injection",
                "index",
                "value",
                "result",
                "msg",
            ],
        )

        def pre_run(params: Params) -> list:
            record = self._get_valid_args()
            if params.is_injection:
                record[params.index] = params.value
            return record

        def post_run(params: Params, instance: FetchedInfo) -> None:
            record = self._get_valid_args()
            if params.is_injection:
                record[params.index] = params.value
            self.assertEqual(record[0], instance.world_id)
            self.assertEqual(record[1], instance.world_name)
            self.assertEqual(record[2], instance.world_url)
            self.assertEqual(record[3], instance.description)
            self.assertEqual(record[4], instance.author_id)
            self.assertEqual(record[5], instance.author_name)
            self.assertEqual(record[6], instance.favorite_id)
            self.assertEqual(record[7], instance.favorite_group)
            self.assertEqual(record[8], instance.is_favorited)
            self.assertEqual(record[9], instance.release_status)
            self.assertEqual(record[10], instance.featured)
            self.assertEqual(record[11], instance.image_url)
            self.assertEqual(record[12], instance.thmbnail_image_url)
            self.assertEqual(record[13], instance.version)
            self.assertEqual(record[14], instance.star)
            self.assertEqual(record[15], instance.visit)
            self.assertEqual(record[16], instance.published_at)
            self.assertEqual(record[17], instance.lab_published_at)
            self.assertEqual(record[18], instance.created_at)
            self.assertEqual(record[19], instance.updated_at)
            self.assertEqual(record[20], instance.registered_at)

            self.assertTrue(re.search("wrld_.*", instance.world_id))
            if instance.published_at:
                datetime.fromisoformat(instance.published_at)
            if instance.lab_published_at:
                datetime.fromisoformat(instance.lab_published_at)
            if instance.created_at:
                datetime.fromisoformat(instance.created_at)
            if instance.updated_at:
                datetime.fromisoformat(instance.updated_at)
            if instance.registered_at:
                datetime.fromisoformat(instance.registered_at)

        params_list: list[Params] = [
            Params(False, None, None, None, "positive case"),
            Params(True, 16, "", None, "published_at is empty"),
            Params(True, 17, "", None, "lab_published_at is empty"),
            Params(True, 18, "", None, "created_at is empty"),
            Params(True, 19, "", None, "updated_at is empty"),
            Params(True, 20, "", None, "registered_at is empty"),
            Params(True, 0, -1, ValueError, "world_id is invalid"),
            Params(True, 1, -1, ValueError, "world_name is invalid"),
            Params(True, 2, -1, ValueError, "world_url is invalid"),
            Params(True, 3, -1, ValueError, "description is invalid"),
            Params(True, 4, -1, ValueError, "author_id is invalid"),
            Params(True, 5, -1, ValueError, "author_name is invalid"),
            Params(True, 6, -1, ValueError, "favorite_id is invalid"),
            Params(True, 7, -1, ValueError, "favorite_group is invalid"),
            Params(True, 8, -1, ValueError, "is_favorited is invalid"),
            Params(True, 9, -1, ValueError, "release_status is invalid"),
            Params(True, 10, "invalid value", ValueError, "featured is invalid"),
            Params(True, 11, -1, ValueError, "image_url is invalid"),
            Params(True, 12, -1, ValueError, "thmbnail_image_url is invalid"),
            Params(True, 13, "invalid value", ValueError, "version is invalid"),
            Params(True, 14, "invalid value", ValueError, "star is invalid"),
            Params(True, 15, "invalid value", ValueError, "visit is invalid"),
            Params(True, 16, -1, ValueError, "published_at is invalid"),
            Params(True, 17, -1, ValueError, "lab_published_at is invalid"),
            Params(True, 18, -1, ValueError, "created_at is invalid"),
            Params(True, 19, -1, ValueError, "updated_at is invalid"),
            Params(True, 20, -1, ValueError, "registered_at is invalid"),
            Params(True, 0, "invalid world_id str", ValueError, "world_id is invalid"),
            Params(True, 16, "invalid published_at str", ValueError, "published_at is invalid"),
            Params(True, 17, "invalid lab_published_at str", ValueError, "lab_published_at is invalid"),
            Params(True, 18, "invalid created_at str", ValueError, "created_at is invalid"),
            Params(True, 19, "invalid updated_at str", ValueError, "updated_at is invalid"),
            Params(True, 20, "invalid registered_at str", ValueError, "registered_at is invalid"),
        ]
        for params in params_list:
            with self.subTest(params.msg):
                instance = None
                record = pre_run(params)
                if not params.result:
                    instance = FetchedInfo(*record)
                    post_run(params, instance)
                else:
                    with self.assertRaises(params.result):
                        instance = FetchedInfo(*record)

    def test_to_dict(self):
        record = self._get_valid_args()
        instance = FetchedInfo(*record)
        expect = {
            "world_id": record[0],
            "world_name": record[1],
            "world_url": record[2],
            "description": record[3],
            "author_id": record[4],
            "author_name": record[5],
            "favorite_id": record[6],
            "favorite_group": record[7],
            "is_favorited": record[8],
            "release_status": record[9],
            "featured": record[10],
            "image_url": record[11],
            "thmbnail_image_url": record[12],
            "version": record[13],
            "star": record[14],
            "visit": record[15],
            "published_at": record[16],
            "lab_published_at": record[17],
            "created_at": record[18],
            "updated_at": record[19],
            "registered_at": record[20],
        }
        actual = instance.to_dict()
        self.assertEqual(expect, actual)

    def test_create(self):
        mock_freezegun = self.enterContext(freezegun.freeze_time("2024-09-05T12:34:56.789000"))

        def to_utc(date_at_str: str) -> str:
            jst = datetime.fromisoformat(date_at_str)
            utc = jst + timedelta(hours=-9)
            return utc.isoformat()

        record = self._get_valid_args()
        fetched_dict = {
            "id": record[0],
            "name": record[1],
            # "world_url": record[2],
            "description": record[3],
            "authorId": record[4],
            "authorName": record[5],
            "favoriteId": record[6],
            "favoriteGroup": record[7],
            # "is_favorited": record[8],
            "releaseStatus": record[9],
            "featured": record[10],
            "imageUrl": record[11],
            "thumbnailImageUrl": record[12],
            "version": record[13],
            "favorites": record[14],
            "visits": record[15],
            "publicationDate": to_utc(record[16]),
            "labsPublicationDate": to_utc(record[17]),
            "created_at": to_utc(record[18]),
            "updated_at": to_utc(record[19]),
            # "registered_at": record[20],
        }
        instance = FetchedInfo.create(fetched_dict)
        expect = {
            "world_id": record[0],
            "world_name": record[1],
            "world_url": f"https://vrchat.com/home/world/{record[0]}",
            "description": record[3],
            "author_id": record[4],
            "author_name": record[5],
            "favorite_id": record[6],
            "favorite_group": record[7],
            "is_favorited": record[8],
            "release_status": record[9],
            "featured": record[10],
            "image_url": record[11],
            "thmbnail_image_url": record[12],
            "version": record[13],
            "star": record[14],
            "visit": record[15],
            "published_at": record[16],
            "lab_published_at": record[17],
            "created_at": record[18],
            "updated_at": record[19],
            "registered_at": record[20],
        }
        actual = instance.to_dict()
        self.assertEqual(expect, actual)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
