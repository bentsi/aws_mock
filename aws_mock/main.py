from uuid import uuid4

from flask import Flask, request

from aws_mock.lib import extract_tags, get_region_name_from_hostname, set_debug
from aws_mock.requests.attach_internet_gateway import attach_internet_gateway
from aws_mock.requests.authorize_security_group_ingress import authorize_security_group_ingress
from aws_mock.requests.copy_image import copy_image
from aws_mock.requests.create_internet_gateway import create_internet_gateway
from aws_mock.requests.create_security_group import create_security_group
from aws_mock.requests.create_subnet import create_subnet
from aws_mock.requests.create_tags import create_tags
from aws_mock.requests.create_vpc import create_vpc
from aws_mock.requests.modify_vpc_attribute import modify_vpc_attribute
from aws_mock.requests.describe_availability_zones import describe_availability_zones
from aws_mock.requests.describe_images import describe_images
from aws_mock.requests.describe_instances import describe_instances
from aws_mock.requests.describe_internet_gateways import describe_internet_gateways
from aws_mock.requests.describe_key_pairs import describe_key_pairs
from aws_mock.requests.describe_route_tables import describe_route_tables
from aws_mock.requests.describe_security_groups import describe_security_groups
from aws_mock.requests.describe_subnets import describe_subnets
from aws_mock.requests.describe_vpcs import describe_vpcs
from aws_mock.requests.import_key_pair import import_key_pair
from aws_mock.requests.modify_subnet_attribute import modify_subnet_attribute
from aws_mock.requests.run_instances import run_instances


app = set_debug(Flask(__name__))


@app.context_processor
def action_context():
    return {
        "action": request.form.get("Action"),
        "request_id": str(uuid4()),
    }


@app.route("/", methods=['POST'])
def index():  # pylint: disable=too-many-return-statements
    region_name = get_region_name_from_hostname(hostname=request.headers["Host"])

    match request.form["Action"]:
        case "RunInstances":
            return run_instances(
                count=int(request.form["MaxCount"]),
                instance_spec={
                    "image_id": request.form["ImageId"],
                    "instance_type": request.form.get("InstanceType", "m1.small"),
                    "key_name": request.form["KeyName"],
                    "subnet_id": request.form["NetworkInterface.1.SubnetId"],
                    "security_group_id": request.form["NetworkInterface.1.SecurityGroupId.1"],
                    "mac_address": "06:0f:3a:66:ba:e8",
                    "private_ip": "10.0.1.30",
                    "ipv6_address": "2a05:d016:cf8:de00:82e3:74cc:fd02:efce",
                    "volume_size": request.form.get("BlockDeviceMapping.1.Ebs.VolumeSize", "10"),
                    "tags": extract_tags(form=request.form, prefix="TagSpecification.1."),
                    "client_token": request.form["ClientToken"],
                    "instance_state_code": "0",
                    "instance_state": "pending",
                },
            )
        case "DescribeInstances":
            return describe_instances(
                instance_ids=[value for key, value in request.form.items() if key.startswith("InstanceId.")],
            )
        case "CreateTags":
            return create_tags(
                resource_ids=[value for key, value in request.form.items() if key.startswith("ResourceId.")],
                tags=extract_tags(request.form),
            )
        case "DescribeKeyPairs":
            return describe_key_pairs(key_name=request.form["KeyName.1"])
        case "ImportKeyPair":
            return import_key_pair(key_name=request.form["KeyName"])
        case "CopyImage":
            return copy_image(
                source_region_name=request.form["SourceRegion"],
                source_ami_id=request.form["SourceImageId"],
                target_region_name=region_name,
            )
        case "CreateSubnet":
            return create_subnet(
                region_name=region_name,
                vpc_id=request.form["VpcId"],
                cidr_block=request.form["CidrBlock"],
                ipv6_cidr_block=request.form["Ipv6CidrBlock"],
                availability_zone=request.form["AvailabilityZone"],
            )
        case "DescribeSubnets":
            return describe_subnets(subnet_name=request.form["Filter.1.Value.1"])
        case "ModifySubnetAttribute":
            return modify_subnet_attribute()
        case "ModifyVpcAttribute":
            return modify_vpc_attribute()
        case "CreateVpc":
            return create_vpc(
                cidr_block=request.form["CidrBlock"],
                ipv6_support=bool(request.form["AmazonProvidedIpv6CidrBlock"]),
                tags=extract_tags(request.form, prefix="TagSpecification.1.")
            )
        case "DescribeAvailabilityZones":
            return describe_availability_zones(region_name=region_name)
        case "DescribeImages":
            return describe_images(region_name=region_name)
        case "DescribeVpcs":
            return describe_vpcs()
        case "CreateSecurityGroup":
            return create_security_group(group_name=request.form["GroupName"])
        case "DescribeSecurityGroups":
            return describe_security_groups()
        case "AuthorizeSecurityGroupIngress":
            return authorize_security_group_ingress(security_group_id=request.form["GroupId"])
        case "CreateInternetGateway":
            return create_internet_gateway()
        case "DescribeInternetGateways":
            return describe_internet_gateways(gateway_name=request.form["Filter.1.Value.1"])
        case "AttachInternetGateway":
            return attach_internet_gateway(gateway_id=request.form["InternetGatewayId"], vpc_id=request.form["VpcId"])
        case "DescribeRouteTables":
            return describe_route_tables()
        case action:
            return f"Unknown action: {action}", 400


if __name__ == "__main__":
    app.run(debug=True)
