import unittest
from functools import cached_property

import boto3

from aws_mock.main import app


class AwsMockTestCase(unittest.TestCase):
    region_name = "eu-north-1"

    def setUp(self) -> None:
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()
        self.base_url = "/"

    def _run_query(self, data: dict):
        return self.app.post(self.base_url, data=data)

    @cached_property
    def ec2_resource(self):
        return boto3.resource("ec2", region_name=self.region_name)

    @cached_property
    def ec2_client(self):
        return boto3.client("ec2", region_name=self.region_name)
