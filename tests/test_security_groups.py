from unittest.mock import Mock, patch

from tests.base import AwsMockTestCase


class TestSecurityGroups(AwsMockTestCase):
    @patch("aws_mock.lib.MongoClient")
    @patch("aws_mock.lib.getrandbits")
    def test_create_security_group(self, getrandbits: Mock, mongo: Mock) -> None:
        request_body = {
            "Action": "CreateSecurityGroup",
            "Version": "2016-11-15",
            "GroupDescription": "Security group that is used by SCT",
            "GroupName": "SCT-sg",
            "VpcId": "vpc-0b04728271b54803d",
        }
        getrandbits.return_value = 0x12345
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert b"CreateSecurityGroupResponse" in response.data
        assert b"<return>true</return>" in response.data
        mongo().aws_mock["sg"].insert_one.assert_called_once_with({
            "id": "sg-12345",
            "tags": {"Name": "SCT-sg"},
        })

    @patch("aws_mock.lib.MongoClient")
    def test_describe_security_groups_empty_list(self, mongo: Mock) -> None:
        request_body = {
            "Action": "DescribeSecurityGroups",
            "Version": "2016-11-15",
            "Filter.1.Name": "tag:Name",
            "Filter.1.Value": "SCT-sg",
        }
        mongo().aws_mock["sg"].find.return_value = []
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert b"</DescribeSecurityGroupsResponse>" in response.data
        assert b"</item>" not in response.data
        mongo().aws_mock["sg"].find.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_describe_security_groups_no_tags(self, mongo: Mock) -> None:
        request_body = {
            "Action": "DescribeSecurityGroups",
            "Version": "2016-11-15",
            "Filter.1.Name": "tag:Name",
            "Filter.1.Value": "SCT-sg",
        }
        mongo().aws_mock["sg"].find.return_value = [{"id": "sg-12345"}]
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert b"</DescribeSecurityGroupsResponse>" in response.data
        assert b"<groupId>sg-12345</groupId>" in response.data
        assert b"<ipPermissions/>" in response.data
        assert b"<tagSet/>" in response.data
        mongo().aws_mock["sg"].find.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_describe_security_groups_with_tags(self, mongo: Mock) -> None:
        request_body = {
            "Action": "DescribeSecurityGroups",
            "Version": "2016-11-15",
            "Filter.1.Name": "tag:Name",
            "Filter.1.Value": "SCT-sg",
        }
        mongo().aws_mock["sg"].find.return_value = [{"id": "sg-12345", "tags": {"tag1": "val1"}}]
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert b"</DescribeSecurityGroupsResponse>" in response.data
        assert b"<groupId>sg-12345</groupId>" in response.data
        assert b"<ipPermissions/>" in response.data
        assert b"</tagSet>" in response.data
        assert b"<key>tag1</key>" in response.data
        assert b"<value>val1</value>" in response.data
        mongo().aws_mock["sg"].find.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_describe_security_groups_with_ingress_rules(self, mongo: Mock) -> None:
        request_body = {
            "Action": "DescribeSecurityGroups",
            "Version": "2016-11-15",
            "Filter.1.Name": "tag:Name",
            "Filter.1.Value": "SCT-sg",
        }
        mongo().aws_mock["sg"].find.return_value = [{"id": "sg-12345", "is_ingress_rules_added": True}]
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert b"</DescribeSecurityGroupsResponse>" in response.data
        assert b"<groupId>sg-12345</groupId>" in response.data
        assert b"<ipPermissions/>" not in response.data
        assert b"</ipPermissions>" in response.data
        mongo().aws_mock["sg"].find.assert_called_once()

    @patch("aws_mock.lib.MongoClient")
    def test_authorize_security_group_ingress(self, mongo: Mock) -> None:
        request_body = {
            "Action": "AuthorizeSecurityGroupIngress",
            "Version": "2016-11-15",
            "GroupId": "sg-12345",
            "IpPermissions.1.IpProtocol": "-1",
            "IpPermissions.1.Groups.1.Description": "Allow ALL traffic inside the Security group",
            "IpPermissions.1.Groups.1.GroupId": "sg-0d3de9bc408daec47",
            "IpPermissions.1.Groups.1.UserId": "797456418907",
            "IpPermissions.2.FromPort": "22",
            "IpPermissions.2.ToPort": "22",
            "IpPermissions.2.IpProtocol": "tcp",
            "IpPermissions.2.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.2.IpRanges.1.Description": "SSH connectivity to the instances",
            "IpPermissions.2.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.2.Ipv6Ranges.1.Description": "SSH connectivity to the instances",
            "IpPermissions.3.FromPort": "3000",
            "IpPermissions.3.ToPort": "3000",
            "IpPermissions.3.IpProtocol": "tcp",
            "IpPermissions.3.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.3.IpRanges.1.Description": "Allow Grafana for ALL",
            "IpPermissions.3.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.3.Ipv6Ranges.1.Description": "Allow Grafana for ALL",
            "IpPermissions.4.FromPort": "9042",
            "IpPermissions.4.ToPort": "9042",
            "IpPermissions.4.IpProtocol": "tcp",
            "IpPermissions.4.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.4.IpRanges.1.Description": "Allow CQL for ALL",
            "IpPermissions.4.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.4.Ipv6Ranges.1.Description": "Allow CQL for ALL",
            "IpPermissions.5.FromPort": "9142",
            "IpPermissions.5.ToPort": "9142",
            "IpPermissions.5.IpProtocol": "tcp",
            "IpPermissions.5.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.5.IpRanges.1.Description": "Allow SSL CQL for ALL",
            "IpPermissions.5.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.5.Ipv6Ranges.1.Description": "Allow SSL CQL for ALL",
            "IpPermissions.6.FromPort": "9100",
            "IpPermissions.6.ToPort": "9100",
            "IpPermissions.6.IpProtocol": "tcp",
            "IpPermissions.6.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.6.IpRanges.1.Description": "Allow node_exporter on Db nodes for ALL",
            "IpPermissions.6.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.6.Ipv6Ranges.1.Description": "Allow node_exporter on Db nodes for ALL",
            "IpPermissions.7.FromPort": "8080",
            "IpPermissions.7.ToPort": "8080",
            "IpPermissions.7.IpProtocol": "tcp",
            "IpPermissions.7.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.7.IpRanges.1.Description": "Allow Alternator for ALL",
            "IpPermissions.7.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.7.Ipv6Ranges.1.Description": "Allow Alternator for ALL",
            "IpPermissions.8.FromPort": "9090",
            "IpPermissions.8.ToPort": "9090",
            "IpPermissions.8.IpProtocol": "tcp",
            "IpPermissions.8.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.8.IpRanges.1.Description": "Allow Prometheus for ALL",
            "IpPermissions.8.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.8.Ipv6Ranges.1.Description": "Allow  Prometheus for ALL",
            "IpPermissions.9.FromPort": "9093",
            "IpPermissions.9.ToPort": "9093",
            "IpPermissions.9.IpProtocol": "tcp",
            "IpPermissions.9.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.9.IpRanges.1.Description": "Allow Prometheus Alert Manager For All",
            "IpPermissions.9.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.9.Ipv6Ranges.1.Description": "Allow Prometheus Alert Manager For All",
            "IpPermissions.10.FromPort": "9180",
            "IpPermissions.10.ToPort": "9180",
            "IpPermissions.10.IpProtocol": "tcp",
            "IpPermissions.10.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.10.IpRanges.1.Description": "Allow Prometheus API for ALL",
            "IpPermissions.10.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.10.Ipv6Ranges.1.Description": "Allow Prometheus API for ALL",
            "IpPermissions.11.FromPort": "7000",
            "IpPermissions.11.ToPort": "7000",
            "IpPermissions.11.IpProtocol": "tcp",
            "IpPermissions.11.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.11.IpRanges.1.Description": "Allow Inter-node communication (RPC) for ALL",
            "IpPermissions.11.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.11.Ipv6Ranges.1.Description": "Allow Inter-node communication (RPC) for ALL",
            "IpPermissions.12.FromPort": "7001",
            "IpPermissions.12.ToPort": "7001",
            "IpPermissions.12.IpProtocol": "tcp",
            "IpPermissions.12.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.12.IpRanges.1.Description": "Allow SSL inter-node communication (RPC) for ALL",
            "IpPermissions.12.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.12.Ipv6Ranges.1.Description": "Allow SSL inter-node communication (RPC) for ALL",
            "IpPermissions.13.FromPort": "7199",
            "IpPermissions.13.ToPort": "7199",
            "IpPermissions.13.IpProtocol": "tcp",
            "IpPermissions.13.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.13.IpRanges.1.Description": "Allow JMX management for ALL",
            "IpPermissions.13.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.13.Ipv6Ranges.1.Description": "Allow JMX management for ALL",
            "IpPermissions.14.FromPort": "10001",
            "IpPermissions.14.ToPort": "10001",
            "IpPermissions.14.IpProtocol": "tcp",
            "IpPermissions.14.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.14.IpRanges.1.Description": "Allow Scylla Manager Agent REST API  for ALL",
            "IpPermissions.14.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.14.Ipv6Ranges.1.Description": "Allow Scylla Manager Agent REST API for ALL",
            "IpPermissions.15.FromPort": "56090",
            "IpPermissions.15.ToPort": "56090",
            "IpPermissions.15.IpProtocol": "tcp",
            "IpPermissions.15.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.15.IpRanges.1.Description": "Allow Scylla Manager Agent version 2.1 Prometheus API for ALL",
            "IpPermissions.15.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.15.Ipv6Ranges.1.Description":
                "Allow Scylla Manager Agent version 2.1 Prometheus API for ALL",
            "IpPermissions.16.IpProtocol": "-1",
            "IpPermissions.16.IpRanges.1.CidrIp": "172.0.0.0/11",
            "IpPermissions.16.IpRanges.1.Description": "Allow traffic from Scylla Cloud lab while VPC peering for ALL",
            "IpPermissions.17.FromPort": "5080",
            "IpPermissions.17.ToPort": "5080",
            "IpPermissions.17.IpProtocol": "tcp",
            "IpPermissions.17.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.17.IpRanges.1.Description": "Allow Scylla Manager HTTP API for ALL",
            "IpPermissions.17.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.17.Ipv6Ranges.1.Description": "Allow Scylla Manager HTTP API for ALL",
            "IpPermissions.18.FromPort": "5443",
            "IpPermissions.18.ToPort": "5443",
            "IpPermissions.18.IpProtocol": "tcp",
            "IpPermissions.18.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.18.IpRanges.1.Description": "Allow Scylla Manager HTTPS API for ALL",
            "IpPermissions.18.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.18.Ipv6Ranges.1.Description": "Allow Scylla Manager HTTPS API for ALL",
            "IpPermissions.19.FromPort": "5090",
            "IpPermissions.19.ToPort": "5090",
            "IpPermissions.19.IpProtocol": "tcp",
            "IpPermissions.19.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.19.IpRanges.1.Description": "Allow Scylla Manager Agent Prometheus API for ALL",
            "IpPermissions.19.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.19.Ipv6Ranges.1.Description": "Allow Scylla Manager Agent Prometheus API for ALL",
            "IpPermissions.20.FromPort": "5112",
            "IpPermissions.20.ToPort": "5112",
            "IpPermissions.20.IpProtocol": "tcp",
            "IpPermissions.20.IpRanges.1.CidrIp": "0.0.0.0/0",
            "IpPermissions.20.IpRanges.1.Description": "Allow Scylla Manager pprof Debug For ALL",
            "IpPermissions.20.Ipv6Ranges.1.CidrIpv6": "::/0",
            "IpPermissions.20.Ipv6Ranges.1.Description": "Allow Scylla Manager pprof Debug For ALL",
        }
        mongo().aws_mock["sg"].find_one.return_value = {"_id": "MOCKED_ID", "id": "sg-12345"}
        with self.app as client:
            response = client.post(self.base_url, data=request_body)
        assert b"</AuthorizeSecurityGroupIngressResponse>" in response.data
        assert b"<groupId>sg-12345</groupId>" in response.data
        mongo().aws_mock["sg"].update_one.assert_called_once_with(
            filter={"_id": "MOCKED_ID"},
            update={"$set": {"is_ingress_rules_added": True}},
        )
