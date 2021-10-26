import logging

from flask import render_template
from aws_mock.lib import get_aws_mock_db, get_region_name_from_hostname


MASTER_REGION = "eu-west-2"

LOGGER = logging.getLogger(__name__)


def describe_images(hostname) -> str:
    region = get_region_name_from_hostname(hostname=hostname)

    LOGGER.debug("Searching for saved images...")
    if region == MASTER_REGION or get_aws_mock_db()["ami"].count():
        LOGGER.debug("Describing default image...")
        ami_item = render_template("responses/describe_images_default_ami_item.xml")
    else:
        LOGGER.debug("No images were found.")
        ami_item = ""
    return render_template("responses/describe_images.xml", ami_item=ami_item)
