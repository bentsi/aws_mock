from unittest.mock import Mock, patch

from tests.base import AwsMockTestCase


class TestDescribeVpc(AwsMockTestCase):
    def setUp(self):
        super().setUp()
        self.vpc_id = "vpc-12345"
        self.request_body = {
            "Action": "DescribeVpcs",
            "Version": "2016-11-15",
            "VpcId": self.vpc_id,
            "CidrBlock": "10.0.0.0/16",
            "AmazonProvidedIpv6CidrBlock": True,
        }

    @patch("aws_mock.lib.MongoClient")
    def test_describe_vpc(self, mongo: Mock) -> None:
        collection = mongo().aws_mock["vpc"]
        collection.find_one.return_value = {"_id": "MOCKED_ID", "id": self.request_body["VpcId"]}
        with self.app as client:
            response = client.post(self.base_url, data=self.request_body)
        assert b"cidrBlock" in response.data
        assert b"<vpcId>vpc-12345</vpcId>" in response.data
