from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from schema.state import AWSItemState
from schema.tags import AWSTag
from utils.misc import random_string


class AWSArchitectureType(Enum):
    x86_64 = 'x86_64'


class AWSImageType(Enum):
    machine = 'machine'


class AWSDeviceType(Enum):
    ebs = 'ebs'


class AWSVolumeType(Enum):
    gp2 = 'gp2'


class AWSBlockDeviceMappingItemEbs(BaseModel):
    snapshotId: str = Field(default_factory=lambda: 'snap-' + random_string(17))
    volumeSize: int
    deleteOnTermination: bool = False
    volumeType: AWSVolumeType = None
    encrypted: bool = False


class AWSBlockDeviceMappingItem(BaseModel):
    deviceName: str
    virtualName: str = None
    ebs: AWSBlockDeviceMappingItemEbs = None


class AWSVirtualizationType(Enum):
    hvm = 'hvm'


class AWSHypervisor(Enum):
    xen = 'xen'


class AWSImage(BaseModel):
    imageId: str
    name: str
    imageLocation: str
    imageState: str = AWSItemState.available
    imageOwnerId: int
    creationDate: str  # 2021-09-27T07:30:49.000Z
    isPublic: bool
    architecture: AWSArchitectureType = AWSArchitectureType.x86_64
    imageType: AWSImageType = AWSImageType.machine
    sriovNetSupport: str = 'simple'
    description: str
    rootDeviceType: AWSDeviceType = AWSDeviceType.ebs
    rootDeviceName: str
    blockDeviceMapping: List[AWSBlockDeviceMappingItem]
    virtualizationType: AWSVirtualizationType = AWSVirtualizationType.hvm
    tagSet: List[AWSTag]
    hypervisor: AWSHypervisor = AWSHypervisor.xen
    enaSupport: bool = True
    platformDetails: str = 'Linux/UNIX'
    usageOperation: str = 'RunInstances'
