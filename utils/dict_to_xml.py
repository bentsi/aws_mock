import uuid
from enum import Enum
from typing import List, Any, Dict

import pydantic


def _default_to_xml(data: Any, output: List[str], name: str):
    if data is None:
        output.append('</' + name + '>')
        return
    output.append('<' + name + '>')
    if isinstance(data, bool):
        if data:
            output.append('true')
        else:
            output.append('false')
    elif isinstance(data, str):
        output.append(data)
    elif isinstance(data, uuid.UUID):
        output.append(str(data))
    elif isinstance(data, (int, float)):
        output.append(str(data))
    else:
        raise ValueError("Unknown type")
    output.append('</' + name + '>')


def _list_to_xml(data: list, output: List[str], name: str) -> str:
    output.append('<%s>' % (name,))
    for item in data:
        if isinstance(item, dict):
            _dict_to_xml(item, name='item', output=output)
        elif isinstance(item, list):
            _list_to_xml(item, name='item', output=output)
        elif isinstance(item, Enum):
            _default_to_xml(item.value, name='item', output=output)
        else:
            _default_to_xml(item, name='item', output=output)
    output.append('</%s>' % (name,))
    return ''.join(output)


def _dict_to_xml(data: dict, output: List[str], name: str = '', attrs: Dict[str, str] = None):
    if name:
        attrs_data = []
        if attrs:
            attrs_data.append('')
            for attr_name, attr_value in attrs.items():
                attrs_data.append('%s="%s"' % (attr_name, attr_value))
        output.append('<%s%s>' % (name, ' '.join(attrs_data)))
    for item_name, item in data.items():
        if isinstance(item, dict):
            _dict_to_xml(item, name=item_name, output=output)
        elif isinstance(item, list):
            _list_to_xml(item, name=item_name, output=output)
        elif isinstance(item, Enum):
            _default_to_xml(item.value, name=item_name, output=output)
        else:
            _default_to_xml(item, name=item_name, output=output)
    if name:
        output.append('</%s>' % (name,))


def object_to_xml(data: pydantic.BaseModel, final: bool = True):
    output = ['<?xml version="1.0" encoding="UTF-8"?>'] if final else []
    attrs = {'xmlns': "http://ec2.amazonaws.com/doc/2016-11-15/"} if final else None
    _dict_to_xml(
        data.dict(exclude_none=True),
        output=output,
        name=type(data).__name__,
        attrs=attrs)
    return ''.join(output)
