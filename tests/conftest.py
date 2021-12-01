from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import boto3
import pytest

from aws_mock.main import app

if TYPE_CHECKING:
    from typing import Callable, TypeAlias

    from flask.testing import FlaskClient
    from werkzeug.test import TestResponse
    from mypy_boto3_ec2 import EC2Client, EC2ServiceResource

    RunQueryFunc: TypeAlias = Callable[[dict], TestResponse]


REGION_NAME = "eu-north-1"
BASE_URL = "/"


def pytest_addoption(parser):
    parser.addoption("--all", action="store_true", default=False, help="Run all tests (incl. integration tests)")


@pytest.fixture(scope="session")
def run_all_tests(request) -> bool:
    return request.config.getoption("--all")


@pytest.fixture(scope="session")
def client() -> FlaskClient:
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    return app.test_client()


@pytest.fixture(scope="session")
def run_query(client: FlaskClient) -> RunQueryFunc:  # pylint: disable=redefined-outer-name
    def _run_query(data: dict) -> TestResponse:
        with client:
            return client.post(BASE_URL, data=data)
    return _run_query


@pytest.fixture
def mongo() -> Mock:
    with patch("aws_mock.lib.MongoClient") as mock:
        yield mock


@pytest.fixture
def getrandbits() -> Mock:
    with patch("aws_mock.lib.getrandbits") as mock:
        yield mock


@pytest.fixture(scope="session")
def ec2_client(run_all_tests: bool) -> EC2Client:  # pylint: disable=redefined-outer-name
    if not run_all_tests:
        pytest.skip(msg="This test requires a running AWS Mock service")
    return boto3.client("ec2", region_name=REGION_NAME)


@pytest.fixture(scope="session")
def ec2_resource(run_all_tests: bool) -> EC2ServiceResource:  # pylint: disable=redefined-outer-name
    if not run_all_tests:
        pytest.skip(msg="This test requires a running AWS Mock service")
    return boto3.resource("ec2", region_name=REGION_NAME)
