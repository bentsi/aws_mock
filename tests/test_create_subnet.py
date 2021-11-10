from unittest.mock import Mock, patch

from tests.base import AwsMockTestCase


class TestCreateSubnet(AwsMockTestCase):
    def _create_subnet(self):
        response = self._run_query(data={
            'Action': 'CreateSubnet',
            'Version': '2016-11-15',
            'CidrBlock': '10.0.0.0/22',
            'Ipv6CidrBlock': '',
            'VpcId': 'vpc-0b04728271b54803d',
            'AvailabilityZone': f'{self.region_name}a',
        })
        assert b"CreateSubnetResponse" in response.data
        assert b"<state>available</state>" in response.data

    def _describe_subnets(self):
        response = self._run_query(data={
            'Action': 'DescribeSubnets',
            'Filter.1.Name': 'tag:Name',
            'Filter.1.Value.1': f'SCT-subnet-{self.region_name}a',
        })
        assert b'DescribeSubnetsResponse' in response.data

    def _modify_subnet_attributes(self):
        response = self._run_query(data={
            'Action': 'ModifySubnetAttribute',
            'Version': '2016-11-15',
            'MapPublicIpOnLaunch.Value': 'true',
            'SubnetId': 'subnet-0bec8219a55cf9bb4',
        })
        assert b'ModifySubnetAttributeResponse' in response.data
        assert b'<return>true</return>' in response.data

    @patch("aws_mock.lib.MongoClient")
    def test_create_subnet(self, mongo: Mock) -> None:
        self._create_subnet()
        subnet_collection = mongo().aws_mock["subnet"]
        subnet_collection.insert_one.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_describe_subnets(self, mongo: Mock) -> None:
        self._describe_subnets()
        subnet_collection = mongo().aws_mock["subnet"]
        subnet_collection.find.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_modify_subnet_attributes(self, mongo: Mock) -> None:
        self._modify_subnet_attributes()
        subnet_collection = mongo().aws_mock["subnet"]
        subnet_collection.find.assert_not_called()

    def test_create_subnet_with_boto3(self):  # pylint: disable=no-self-use
        result = self.ec2_client.create_subnet(
            CidrBlock='10.0.0.0/24',
            Ipv6CidrBlock='2406:da16:5be:8800::/64',
            AvailabilityZone='eu-north-1a',
            VpcId='vpc-0000000001',
        )
        assert result

    def test_describe_subnets_with_boto3(self):
        subnet_name = 'my-subnet'
        result = self.ec2_client.describe_subnets(Filters=[{"Name": "tag:Name", "Values": [subnet_name]}])
        assert not result['Subnets']
        result = self.ec2_client.create_subnet(
            CidrBlock='10.0.0.0/24',
            Ipv6CidrBlock='2406:da16:5be:8800::/64',
            AvailabilityZone=f'{self.region_name}a',
            VpcId='vpc-0000000001',
        )
        subnet_id = result["Subnet"]["SubnetId"]
        subnet = self.ec2_resource.Subnet(subnet_id)
        subnet.create_tags(Tags=[{"Key": "Name", "Value": subnet_name}])
        result = self.ec2_client.describe_subnets(Filters=[{"Name": "tag:Name", "Values": [subnet_name]}])
        assert result['Subnets']

    def test_modify_subnet_attribute_with_boto3(self):
        response = self.ec2_client.modify_subnet_attribute(
            MapPublicIpOnLaunch={"Value": True},
            SubnetId='subnet-0000000001',
        )
        assert response["ResponseMetadata"]
