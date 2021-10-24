import uuid
from enum import Enum
from typing import List

from pydantic import BaseModel

from schema.state import AWSItemState
from schema.tags import AWSTag


class AWSAssociationState(Enum):
    associated = 'associated'


class AWSCidrBlockState(BaseModel):
    state: AWSAssociationState


class AWSSubnetAssociation(BaseModel):
    cidrBlock: str
    associationId: str
    cidrBlockState: AWSCidrBlockState


class AWSIpv6CidrBlockAssociation(BaseModel):
    ipv6CidrBlock: str
    associationId: str
    ipv6CidrBlockState: AWSCidrBlockState
    ipv6Pooc: str
    networkBorderGroup: str


class AWSVpc(BaseModel):
    vpcId: uuid.UUID
    ownerId: int
    state: AWSItemState = AWSItemState.available
    cidrBlock: str  # 10.0.0.0/16
    cidrBlockAssociationSet: List[AWSSubnetAssociation]
    ipv6CidrBlockAssociationSet: List[AWSIpv6CidrBlockAssociation]
    dhcpOptionsId: str
    tagSet: List[AWSTag]
    instanceTenancy: str
    isDefault: bool
