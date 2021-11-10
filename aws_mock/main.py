from uuid import uuid4

from flask import Flask, request, render_template

from aws_mock.lib import extract_tags, get_region_name_from_hostname
from aws_mock.describe_instances import describe_instances
from aws_mock.run_instances import run_instances
from aws_mock.create_tags import create_tags
from aws_mock.describe_key_pairs import describe_key_pairs
from aws_mock.import_key_pair import import_key_pair
from aws_mock.copy_image import copy_image
from aws_mock.create_subnet import create_subnet
from aws_mock.describe_subnets import describe_subnets
from aws_mock.modify_subnet_attribute import modify_subnet_attribute
from aws_mock.create_vpc import create_vpc
from aws_mock.describe_availability_zones import describe_availability_zones
from aws_mock.describe_images import describe_images
from aws_mock.describe_vpcs import describe_vpcs
from aws_mock.create_security_group import create_security_group
from aws_mock.describe_security_groups import describe_security_groups
from aws_mock.authorize_security_group_ingress import authorize_security_group_ingress
from aws_mock.create_internet_gateway import create_internet_gateway
from aws_mock.describe_internet_gateways import describe_internet_gateways
from aws_mock.attach_internet_gateway import attach_internet_gateway
from aws_mock.describe_route_tables import describe_route_tables


app = Flask(__name__)


@app.context_processor
def add_request_id():
    return {"request_id": str(uuid4())}


@app.route("/", methods=['POST'])
def index():  # pylint: disable=too-many-return-statements
    match request.form["Action"]:
        case "RunInstances":
            return run_instances(request_data=request.form)
        case "DescribeInstances":
            return describe_instances(request_data=request.form)
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
                source_region=request.form["SourceRegion"],
                source_ami_id=request.form["SourceImageId"],
                target_region=get_region_name_from_hostname(hostname=request.headers["Host"])
            )
        case "CreateSubnet":
            return create_subnet(
                region_name=get_region_name_from_hostname(hostname=request.headers["Host"]),
                vpc_id=request.form["VpcId"],
                cidr=request.form["CidrBlock"],
                ipv6_cidr=request.form["Ipv6CidrBlock"],
                availability_zone=request.form["AvailabilityZone"],
            )
        case "DescribeSubnets":
            return describe_subnets(subnet_name=request.form["Filter.1.Value.1"])
        case "ModifySubnetAttribute":
            return modify_subnet_attribute()
        case "CreateVpc":
            return create_vpc(
                cidr=request.form["CidrBlock"],
                ipv6_support=bool(request.form["AmazonProvidedIpv6CidrBlock"]),
                tags=extract_tags(request.form)
            )
        case "DescribeAvailabilityZones":
            return describe_availability_zones(hostname=request.headers['Host'])
        case "DescribeImages":
            return describe_images(hostname=request.headers["Host"])
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
            return attach_internet_gateway()
        case "DescribeRouteTables":
            return describe_route_tables()
        case action:
            return f"Unknown action: {action}", 400


@app.route("/scylla-qa-ec2.pub")
def return_scylla_qa_ec2_public_key():
    return render_template("responses/scylla-qa-ec2.pub")


@app.route("/scylla-qa-ec2")
def return_scylla_qa_ec2_private_key():
    return render_template("responses/scylla-qa-ec2")
