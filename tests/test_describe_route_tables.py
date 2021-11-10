from unittest.mock import Mock, patch

from tests.base import AwsMockTestCase


class TestDescribeRouteTables(AwsMockTestCase):
    def _describe_route_tables1(self):
        response = self._run_query(data={
            'Action': 'DescribeRouteTables',
            'Filter.1.Name': 'tag:Name',
            'Filter.1.Value.1': f'SCT-{self.region_name}',
        })
        assert b'DescribeRouteTablesResponse' in response.data

    def _describe_route_tables2(self):
        response = self._run_query(data={
            'Action': 'DescribeRouteTables',
            'Filter.1.Name': 'vpc-id',
            'Filter.1.Value.1': 'vpc-0b04728271b54803d',
        })
        assert b'DescribeRouteTablesResponse' in response.data

    @patch("aws_mock.lib.MongoClient")
    def test_describe_route_tables1(self, mongo: Mock) -> None:
        self._describe_route_tables1()
        subnet_collection = mongo().aws_mock["subnet"]
        subnet_collection.find.assert_not_called()

    @patch("aws_mock.lib.MongoClient")
    def test_describe_route_tables2(self, mongo: Mock) -> None:
        self._describe_route_tables2()
        subnet_collection = mongo().aws_mock["subnet"]
        subnet_collection.find.assert_not_called()

    def test_describe_route_tables_with_boto3(self):
        route_table_name = 'my-subnet'
        result = self.ec2_client.describe_route_tables(Filters=[{"Name": "tag:Name",
                                                                 "Values": [route_table_name]}])
        assert result['RouteTables']
        result = self.ec2_client.describe_route_tables(Filters=[{"Name": "vpc-id",
                                                                 "Values": ['vpc-0b04728271b54803d']}])
        assert result['RouteTables']
