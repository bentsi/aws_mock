from flask import Flask, request
from aws_mock.describe_instances import describe_instances
from aws_mock.run_instances import run_instances

app = Flask(__name__)


@app.route("/", methods=['POST'])
def index():
    action = request.form["Action"]
    match request.form["Action"]:
        case "RunInstances":
            return run_instances(request_data=request.form)
        case "DescribeInstances":
            return describe_instances(request_data=request.form)

        case _:
            return f"Unknown action: {action}", 400
