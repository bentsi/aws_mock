from uuid import uuid4

from flask import Flask, request, render_template

from aws_mock.lib import aws_extract_request_data, get_aws_mock_db, get_collection_name, get_az_id
from aws_mock.run_instances import generate_resource_id

app = Flask(__name__)
subnet_collection_name = 'subnet'


def add_subnet(cidr: str, ipv6_cidr: str, vpc_id: str, az: str) -> str:
    subnet_collection = get_aws_mock_db()[subnet_collection_name]
    subnet_id = generate_resource_id(prefix=subnet_collection_name)
    subnet_body = render_template(
        'responses/subnet.xml',
        subnet_id=subnet_id,
        cidr=cidr,
        ipv6_cidr=ipv6_cidr,
        vpc_id=vpc_id,
        az=az,
        az_id=get_az_id(az)
    )
    subnet_collection.insert({
        "id": subnet_id,
        "tags": {},
        "body": subnet_body
    })
    return subnet_body


def create_subnet(request_data: dict):
    cidr = request_data['CidrBlock']
    ipv6_cidr = request_data['Ipv6CidrBlock']
    vpc_id = request_data['VpcId']
    az = request_data['AvailabilityZone']
    subnet_body = add_subnet(cidr=cidr, ipv6_cidr=ipv6_cidr, vpc_id=vpc_id, az=az)
    return render_template(
        'responses/create_subnet.xml',
        request_id=str(uuid4()),
        subnet_body=subnet_body
    )


def describe_subnets(request_data: dict):
    subnet_name = request_data['Filter'][0]['Value'][0]
    subnet_bodies = []
    for subnet_record in get_aws_mock_db()[subnet_collection_name].find({'tags.Name': subnet_name}):
        subnet_bodies.append(subnet_record['body'])
    return render_template(
        'responses/describe_subnets.xml',
        request_id=str(uuid4()),
        subnet_bodies=subnet_bodies,
    )


def modify_subnet_attribute(request_data: dict):
    return render_template(
        'responses/modify_subnet_attributes.xml',
        request_id=str(uuid4())
    )


@app.route("/", methods=["POST"])
def index():
    request_data = aws_extract_request_data(request.form)
    match request_data["Action"]:
        case "CreateSubnet":
            return create_subnet(request_data)
        case "DescribeSubnets":
            return describe_subnets(request_data)
        case "ModifySubnetAttribute":
            return modify_subnet_attribute(request_data)


if __name__ == "__main__":
    app.run(debug=True)
