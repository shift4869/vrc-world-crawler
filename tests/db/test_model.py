import sys
import unittest

from mock import MagicMock, patch

from vrc_world_crawler.db.model import FavoriteWorld


class TestFavoriteWorld(unittest.TestCase):
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

    def _check_member(self, expect: list, actual: FavoriteWorld) -> None:
        self.assertEqual(expect[0], actual.world_id)
        self.assertEqual(expect[1], actual.world_name)
        self.assertEqual(expect[2], actual.world_url)
        self.assertEqual(expect[3], actual.description)
        self.assertEqual(expect[4], actual.author_id)
        self.assertEqual(expect[5], actual.author_name)
        self.assertEqual(expect[6], actual.favorite_id)
        self.assertEqual(expect[7], actual.favorite_group)
        self.assertEqual(expect[8], actual.is_favorited)
        self.assertEqual(expect[9], actual.release_status)
        self.assertEqual(expect[10], actual.featured)
        self.assertEqual(expect[11], actual.image_url)
        self.assertEqual(expect[12], actual.thmbnail_image_url)
        self.assertEqual(expect[13], actual.version)
        self.assertEqual(expect[14], actual.star)
        self.assertEqual(expect[15], actual.visit)
        self.assertEqual(expect[16], actual.published_at)
        self.assertEqual(expect[17], actual.lab_published_at)
        self.assertEqual(expect[18], actual.created_at)
        self.assertEqual(expect[19], actual.updated_at)
        self.assertEqual(expect[20], actual.registered_at)

    def test_init(self) -> None:
        record = self._get_valid_args()
        instance = FavoriteWorld(*record)
        self._check_member(record, instance)

    def test_create(self) -> None:
        record = self._get_valid_args()
        args_dict = {
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
        instance = FavoriteWorld.create(args_dict)
        self._check_member(record, instance)

        with self.assertRaises(ValueError):
            instance = FavoriteWorld.create({"invalid_dict": ""})

    def test_repr(self) -> None:
        record = self._get_valid_args()
        instance = FavoriteWorld(*record)
        expect = f"<FavoriteWorld(world_id='{record[0]}')>"
        actual = repr(instance)
        self.assertEqual(expect, actual)

    def test_eq(self) -> None:
        record1 = self._get_valid_args()
        record1[0] = "wrld_world_id1"
        record2 = self._get_valid_args()
        record2[0] = "wrld_world_id2"
        instance1 = FavoriteWorld(*record1)
        instance2 = FavoriteWorld(*record2)
        self.assertTrue(instance1 == instance1)
        self.assertFalse(instance1 == instance2)
        self.assertFalse(instance1 == "Not Same Class")

    def test_to_dict(self) -> None:
        record = self._get_valid_args()
        instance = FavoriteWorld(*record)
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
        self.assertEqual(expect, instance.to_dict())


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
