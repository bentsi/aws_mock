import unittest
from unittest.mock import Mock, patch

import boto3

from aws_mock.create_internet_gateway import app


class TestCreateSubnet(unittest.TestCase):
    region_name = 'eu-north-1'

    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.app = app.test_client()
        self.base_url = '/'

    def _run_query(self, data: dict):
        return self.app.post(self.base_url, data=data)

    @property
    def aws_resource(self):
        return boto3.resource("ec2", region_name=self.region_name)

    @property
    def aws_client(self):
        return boto3.client("ec2", region_name=self.region_name)

    def _create_gateway(self):
        response = self._run_query(data={
            'Action': 'CreateInternetGateway',
            'Version': '2016-11-15',
        })
        assert b"CreateInternetGatewayResponse" in response.data
        assert b"<state>available</state>" in response.data

    def _describe_gateways(self):
        response = self._run_query(data={
            'Action': 'DescribeInternetGateways',
            'Filter.1.Name': 'tag:Name',
            'Filter.1.Value.1': f'SCT-igw-{self.region_name}a',
        })
        assert b'DescribeInternetGateways' in response.data

    @patch("aws_mock.lib.MongoClient")
    def test_create_gateway(self, mongo: Mock) -> None:
        self._create_gateway()
        gateway_collection = mongo().aws_mock["igw"]
        gateway_collection.insert.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_describe_gateways(self, mongo: Mock) -> None:
        self._describe_gateways()
        gateway_collection = mongo().aws_mock["gateway"]
        gateway_collection.find.assert_called_once()

    def test_create_gateway_with_boto3(self):
        ec2 = boto3.resource("ec2", region_name="eu-north-1")
        result = ec2.create_internet_gateway()
        assert result['internetGateway']

    def test_describe_gateways_with_boto3(self):
        gateway_name = 'my-gateway'
        result = self.aws_resource.describe_internet_gateways(Filters=[{"Name": "tag:Name", "Values": [gateway_name]}])
        assert not result['gatewaySet']
        result = self.aws_resource.create_internet_gateway()
        gateway_id = result["Subnet"]["SubnetId"]
        gateway = self.aws_resource.Subnet(gateway_id)
        gateway.create_tags(Tags=[{"Key": "Name", "Value": gateway_name}])
        result = self.aws_resource.describe_internet_gateways(Filters=[{"Name": "tag:Name", "Values": [gateway_name]}])
        assert result['gatewaySet']
        result = gateway.attach_to_vpc(VpcId='vpc-00000000001')
        assert result['return']
