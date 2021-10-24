import datetime
import uuid
from typing import List, Dict, Union

import pydantic

from schema.image import AWSImage, AWSBlockDeviceMappingItem, AWSBlockDeviceMappingItemEbs, AWSVolumeType
from utils.misc import random_string, random_int, aws_tags_from_dict


def aws_sct_runner_image(version: str):
    imageOwnerId = random_int(17)
    name = 'sct-runner-' + version
    imageLocation = str(imageOwnerId) + '/' + name
    return AWSImage(
        imageId='ami-' + random_string(17),
        name=name,
        imageLocation=imageLocation,
        imageOwnerId=imageOwnerId,
        creationDate=(datetime.datetime.now() - datetime.timedelta(weeks=24)).strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        isPublic=True,
        description=name,
        rootDeviceName='/dev/sda1',
        blockDeviceMapping=[
            AWSBlockDeviceMappingItem(
                deviceName='/dev/sda1',
                ebs=AWSBlockDeviceMappingItemEbs(
                    volumeSize=80,
                    deleteOnTermination=True,
                    volumeType=AWSVolumeType.gp2.value,
                    encrypted=False,
                ),
            ),
            AWSBlockDeviceMappingItem(
                deviceName='/dev/sdb',
                virtualName='ephemeral0',
            )
        ],
        tagSet=aws_tags_from_dict({
            'Version': version,
            'Name': name,
        }),
    )


class DescribeImagesResponse(pydantic.BaseModel):
    requestId: uuid.UUID
    imagesSet: List[AWSImage]


class CopyImageResponse(pydantic.BaseModel):
    imageId: str
    requestId: uuid.UUID


class ResponseError(pydantic.BaseModel):
    Code: str
    Message: str


class ResponseErrors(pydantic.BaseModel):
    Error: ResponseError


class Respone(pydantic.BaseModel):
    Errors: ResponseErrors
    RequestID: uuid.UUID


def create_error_response(msg: str, code: str):
    return Respone(
        RequestID=uuid.uuid4(),
        Errors=ResponseErrors(
            Error=ResponseError(
                Code=code,
                Message=msg
            )
        )
    )


class ImageDataBase:
    def __init__(self):
        self.images = [
            aws_sct_runner_image('1.5')
        ]

    def copy_image(self, request_data: dict) -> Union[CopyImageResponse, Respone]:
        name = request_data.get('Name', '')
        if 'sct-runner' in name:
            runner_version = name.split('-')[-1]
            image = aws_sct_runner_image(version=runner_version)
            self.images.append(image)
            return CopyImageResponse(
                imageId=image.imageId,
                requestId=uuid.uuid4()
            )
        raise create_error_response(msg='Unknown image type', code='custom.error')

    def describe_images(self, request_data: dict) -> DescribeImagesResponse:
        filters = request_data.get('Filter')
        return DescribeImagesResponse(
            requestId=uuid.uuid4(),
            imagesSet=self.find_image(filters)
        )

    def find_image(self, filters: List[Dict[str, str]]) -> List[AWSImage]:
        output = []
        for image in self.images:
            image_matched = True
            for fl in filters:
                filter_type, filter_name = fl['Name'].split(':', maxsplit=2)
                filter_values = fl['Value']
                filter_matched = False
                if filter_type == 'tag':
                    for tag in image.tagSet:
                        if tag.key == filter_name:
                            if tag.value in filter_values:
                                filter_matched = True
                                break
                if not filter_matched:
                    image_matched = False
            if image_matched:
                output.append(image)
        return output


image_database = ImageDataBase()
