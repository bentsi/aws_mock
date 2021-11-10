from unittest.mock import Mock, patch

from tests.base import AwsMockTestCase


class TestKeyPairs(AwsMockTestCase):
    @patch("aws_mock.lib.MongoClient")
    def test_describe_key_pairs_not_found(self, mongo: Mock) -> None:
        request_body = {
            "Action": "DescribeKeyPairs",
            "Version": "2016-11-15",
            "KeyName.1": "test-key-name",
        }
        mongo().aws_mock["key"].find_one.return_value = None
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert response.status_code == 400
        assert b"<Code>InvalidKeyPair.NotFound</Code>" in response.data
        assert b"test-key-name" in response.data
        mongo().aws_mock["key"].find_one.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_describe_key_pairs(self, mongo: Mock) -> None:
        request_body = {
            "Action": "DescribeKeyPairs",
            "Version": "2016-11-15",
            "KeyName.1": "test-key-name",
        }
        mongo().aws_mock["key"].find_one.return_value = {"id": "key-12345", "name": "test-key-name"}
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert response.status_code == 200
        assert b"</DescribeKeyPairsResponse>" in response.data
        assert b"<keyName>test-key-name</keyName>" in response.data
        assert b"<keyPairId>key-12345</keyPairId>" in response.data
        assert b"<tagSet/>" in response.data
        mongo().aws_mock["key"].find_one.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_describe_key_pairs_with_tags(self, mongo: Mock) -> None:
        request_body = {
            "Action": "DescribeKeyPairs",
            "Version": "2016-11-15",
            "KeyName.1": "test-key-name",
        }
        mongo().aws_mock["key"].find_one.return_value = {
            "id": "key-12345",
            "name": "test-key-name",
            "tags": {"tag1": "val1"},
        }
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert response.status_code == 200
        assert b"</DescribeKeyPairsResponse>" in response.data
        assert b"<keyName>test-key-name</keyName>" in response.data
        assert b"<keyPairId>key-12345</keyPairId>" in response.data
        assert b"</tagSet>" in response.data
        assert b"<key>tag1</key>" in response.data
        assert b"<value>val1</value>" in response.data
        mongo().aws_mock["key"].find_one.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    @patch("aws_mock.lib.getrandbits")
    def test_import_key_pair(self, getrandbits: Mock, mongo: Mock) -> None:
        request_body = {
            "Action": "ImportKeyPair",
            "Version": "2016-11-15",
            "KeyName": "test-key-name",
            "PublicKeyMaterial": "AAA...BBB",
        }
        getrandbits.return_value = 0x12345
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert b"</ImportKeyPairResponse>" in response.data
        assert b"<keyName>test-key-name</keyName>" in response.data
        assert b"<keyPairId>key-12345</keyPairId>" in response.data
        mongo().aws_mock["key"].insert_one.assert_called_once_with({
            "id": "key-12345",
            "name": "test-key-name",
        })
