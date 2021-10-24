import unittest
from unittest.mock import Mock, patch

from aws_mock.create_tags import app


class TestCreateTags(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.app = app.test_client()
        self.base_url = '/'
        self.request_body = {
            "Action": "CreateTags",
            "Version": "2016-11-15",
            "ResourceId.1": "i-12345",
            "Tag.1.Key": "tag1",
            "Tag.1.Value": "val1",
            "Tag.2.Key": "tag2",
            "Tag.2.Value": "val2",
        }

    @patch("aws_mock.create_tags.MongoClient")
    def test_instance_tags(self, mongo: Mock) -> None:
        mongo().aws_mock["i"].find_one.return_value = {"_id": "MOCKED_ID"}
        with self.app as c:
            response = c.post(self.base_url, data=self.request_body)
        assert b"CreateTagsResponse" in response.data
        assert b"<return>true</return>" in response.data
        mongo().aws_mock["i"].find_one.assert_called_once_with({"id": "i-12345"})
        mongo().aws_mock["i"].update_one.assert_called_once_with(
            filter={"_id": "MOCKED_ID"},
            update={"$set": {"tags": {
                "tag1": "val1",
                "tag2": "val2",
            }}},
        )
