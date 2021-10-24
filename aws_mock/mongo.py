import random
import string
from pprint import pformat

from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)


@app.route("/")
def index():
    client = MongoClient()
    client.aws_mock.data.insert_one({"letter": random.choice(string.ascii_letters)})
    return "\n".join(pformat(doc) for doc in client.aws_mock.data.find()) + "\n"
