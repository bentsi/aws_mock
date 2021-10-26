from uuid import uuid4

from flask import Flask, request, render_template
from aws_mock.lib import aws_extract_request_data


app = Flask(__name__)
subnet_collection_name = 'subnet'


def describe_route_tables(request_data: dict):
    return render_template(
        'responses/describe_route_tables.xml',
        request_id=str(uuid4()),
        route_table_id='rtb-0177edc4ef11712e8',
        vpc_id='vpc-0b04728271b54803d',
    )


@app.route("/", methods=["POST"])
def index():
    request_data = aws_extract_request_data(request.form)
    match request_data["Action"]:
        case "DescribeRouteTables":
            return describe_route_tables(request_data)


if __name__ == "__main__":
    app.run(debug=True)
