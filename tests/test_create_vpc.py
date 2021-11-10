from unittest.mock import Mock, patch

from tests.base import AwsMockTestCase


class TestCreateVpc(AwsMockTestCase):
    def setUp(self):
        super().setUp()
        self.vpc_id = "vpc-12345"
        self.request_body = {
            "Action": "CreateVpc",
            "Version": "2016-11-15",
            "CidrBlock": "10.0.0.0/16",
            "AmazonProvidedIpv6CidrBlock": True,
        }

    @patch("aws_mock.lib.MongoClient")
    def test_create_vpc(self, mongo: Mock) -> None:
        collection = mongo().aws_mock["vpc"]
        collection.find.return_value = [{"_id": "MOCKED_ID", "id": "vpc-12345"}]
        with self.app as client:
            response = client.post(self.base_url, data=self.request_body)
        assert b"vpcId" in response.data
        assert b"<cidrBlock>10.0.0.0/16</cidrBlock>" in response.data
