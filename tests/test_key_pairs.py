from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest.mock import Mock

    from tests.conftest import RunQueryFunc


def test_describe_key_pairs_not_found(run_query: RunQueryFunc, mongo: Mock) -> None:
    mongo().aws_mock["key"].find_one.return_value = None
    response = run_query({
        "Action": "DescribeKeyPairs",
        "Version": "2016-11-15",
        "KeyName.1": "test-key-name",
    })
    assert response.status_code == 400
    assert b"<Code>InvalidKeyPair.NotFound</Code>" in response.data
    assert b"test-key-name" in response.data
    mongo().aws_mock["key"].find_one.assert_called_once()


def test_describe_key_pairs(run_query: RunQueryFunc, mongo: Mock) -> None:
    mongo().aws_mock["key"].find_one.return_value = {
        "id": "key-12345",
        "name": "test-key-name",
        "tags": {},
    }
    response = run_query({
        "Action": "DescribeKeyPairs",
        "Version": "2016-11-15",
        "KeyName.1": "test-key-name",
    })
    assert response.status_code == 200
    assert b"</DescribeKeyPairsResponse>" in response.data
    assert b"<keyName>test-key-name</keyName>" in response.data
    assert b"<keyPairId>key-12345</keyPairId>" in response.data
    assert b"<tagSet/>" in response.data
    mongo().aws_mock["key"].find_one.assert_called_once()


def test_describe_key_pairs_with_tags(run_query: RunQueryFunc, mongo: Mock) -> None:
    mongo().aws_mock["key"].find_one.return_value = {
        "id": "key-12345",
        "name": "test-key-name",
        "tags": {"tag1": "val1"},
    }
    response = run_query({
        "Action": "DescribeKeyPairs",
        "Version": "2016-11-15",
        "KeyName.1": "test-key-name",
    })
    assert response.status_code == 200
    assert b"</DescribeKeyPairsResponse>" in response.data
    assert b"<keyName>test-key-name</keyName>" in response.data
    assert b"<keyPairId>key-12345</keyPairId>" in response.data
    assert b"</tagSet>" in response.data
    assert b"<key>tag1</key>" in response.data
    assert b"<value>val1</value>" in response.data
    mongo().aws_mock["key"].find_one.assert_called_once()


def test_import_key_pair(run_query: RunQueryFunc, getrandbits: Mock, mongo: Mock) -> None:
    getrandbits.return_value = 0x12345
    response = run_query({
        "Action": "ImportKeyPair",
        "Version": "2016-11-15",
        "KeyName": "test-key-name",
        "PublicKeyMaterial": "AAA...BBB",
    })
    assert b"</ImportKeyPairResponse>" in response.data
    assert b"<keyName>test-key-name</keyName>" in response.data
    assert b"<keyPairId>key-12345</keyPairId>" in response.data
    mongo().aws_mock["key"].insert_one.assert_called_once_with({
        "id": "key-12345",
        "name": "test-key-name",
        "tags": {},
    })
