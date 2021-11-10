from unittest.mock import Mock, patch

from tests.base import AwsMockTestCase


class TestCreateInternetGateway(AwsMockTestCase):
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
        gateway_collection.insert_one.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_describe_gateways(self, mongo: Mock) -> None:
        self._describe_gateways()
        gateway_collection = mongo().aws_mock["gateway"]
        gateway_collection.find.assert_called_once()

    def test_with_boto3(self):
        gateway_name = 'my-gateway'
        result = self.ec2_client.describe_internet_gateways(Filters=[{"Name": "tag:Name", "Values": [gateway_name]}])
        assert not result['InternetGateways']
        result = self.ec2_client.create_internet_gateway()
        gateway_id = result["InternetGateway"]["InternetGatewayId"]
        gateway = self.ec2_resource.InternetGateway(gateway_id)
        gateway.create_tags(Tags=[{"Key": "Name", "Value": gateway_name}])
        result = self.ec2_client.describe_internet_gateways(Filters=[{"Name": "tag:Name", "Values": [gateway_name]}])
        assert result['InternetGateways']
        result = gateway.attach_to_vpc(VpcId='vpc-00000000001')
        assert result['ResponseMetadata']
