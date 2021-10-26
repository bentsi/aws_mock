from uuid import uuid4

from flask import Flask, request, render_template

from aws_mock.lib import aws_extract_request_data, get_aws_mock_db, get_collection_name, get_az_id
from aws_mock.run_instances import generate_resource_id

app = Flask(__name__)
internet_gw_collection_name = 'igw'


def add_internet_gateway() -> str:
    internet_gw_collection = get_aws_mock_db()[internet_gw_collection_name]
    gateway_id = generate_resource_id(prefix=internet_gw_collection_name)
    gateway_body = render_template(
        'responses/internet_gateway.xml',
        gateway_id=gateway_id,
    )
    internet_gw_collection.insert({
        "id": gateway_id,
        "tags": {},
        "body": gateway_body
    })
    return gateway_body


def create_internet_gateway(request_data: dict):
    gateway_body = add_internet_gateway()
    return render_template(
        'responses/create_internet_gateway.xml',
        request_id=str(uuid4()),
        gateway_body=gateway_body
    )


def describe_internet_gateways(request_data: dict):
    gateway_name = request_data['Filter'][0]['Value'][0]
    gateway_bodies = []
    for gateway_record in get_aws_mock_db()[internet_gw_collection_name].find({'tags.Name': gateway_name}):
        gateway_bodies.append(gateway_record['body'])
    return render_template(
        'responses/describe_internet_gateways.xml',
        request_id=str(uuid4()),
        gateway_bodies=gateway_bodies,
    )


def attache_internet_gateway(request_data: dict):
    return render_template(
        'responses/attach_internet_gateway.xml',
        request_id=str(uuid4()),
    )


@app.route("/", methods=["POST"])
def index():
    request_data = aws_extract_request_data(request.form)
    match request_data["Action"]:
        case "CreateInternetGateway":
            return create_internet_gateway(request_data)
        case "DescribeInternetGateways":
            return describe_internet_gateways(request_data)
        case "AttachInternetGateway":
            return attache_internet_gateway(request_data)


if __name__ == "__main__":
    app.run(debug=True)
