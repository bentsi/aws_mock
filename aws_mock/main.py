from flask import Flask, request

from utils.dict_to_xml import object_to_xml
from utils.misc import aws_extract_request_data
from aws_mock.database.images import image_database


app = Flask(__name__)


@app.route("/", methods=['POST', 'GET', 'PUT'])
def index():
    request_data = aws_extract_request_data(request.form)
    action = request_data.get('Action')
    if action == 'DescribeImages':
        return object_to_xml(image_database.describe_images(request_data))
    if action == 'CopyImage':
        return object_to_xml(image_database.copy_image(request_data))
    return f"Unknown action {action}"
