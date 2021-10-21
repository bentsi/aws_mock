from aws_mock.responses import scylla_qa_ec2_key

from flask import Flask


app = Flask(__name__)


@app.route("/")
def index():
    return "Nginx, uWSGI, and Flask"


@app.route("/scylla-qa-ec2.pub")
def return_scylla_qa_ec2_public_key():
    return scylla_qa_ec2_key.get_public_key()


@app.route("/scylla-qa-ec2")
def return_scylla_qa_ec2_private_key():
    return scylla_qa_ec2_key.get_private_key()
