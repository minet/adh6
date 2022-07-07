# coding=utf-8
import datetime
import decimal
import json
import os
import re
import tempfile

import six

import adh6.entity
from adh6.exceptions import ValidationError

PRIMITIVE_TYPES = (float, bool, bytes, six.text_type, decimal.Decimal) + six.integer_types
NATIVE_TYPES_MAPPING = {
    'int': int,
    'long': int if six.PY3 else long,  # noqa: F821
    'float': float,
    'double': decimal.Decimal,
    'str': str,
    'bool': bool,
    'date': datetime.date,
    'datetime': datetime.datetime,
    'object': object,
}


def serialize_response(obj):
    """Builds a JSON POST object.

    If obj is None, return None.
    If obj is str, int, long, float, bool, return directly.
    If obj is datetime.datetime, datetime.date
        convert to string in iso8601 format.
    If obj is list, sanitize each element in the list.
    If obj is dict, return the dict.
    If obj is swagger model, return the properties dict.

    :param obj: The data to serialize.
    :return: The serialized form of data.
    """
    if obj is None:
        return None
    elif isinstance(obj, PRIMITIVE_TYPES):
        return obj
    elif isinstance(obj, list):
        return [serialize_response(sub_obj)
                for sub_obj in obj]
    elif isinstance(obj, tuple):
        return tuple(serialize_response(sub_obj)
                     for sub_obj in obj)
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    if isinstance(obj, dict):
        obj_dict = obj
    else:
        # Convert model obj to dict except
        # attributes `swagger_types`, `attribute_map`
        # and attributes which value is not None.
        # Convert attribute name to json key in
        # model definition for request.
        obj_dict = {obj.attribute_map[attr]: getattr(obj, attr)
                    for attr, _ in six.iteritems(obj.swagger_types)
                    if getattr(obj, attr) is not None}
        obj_dict['__typename'] = type(obj).__name__
    return {key: serialize_response(val)
            for key, val in six.iteritems(obj_dict)}


def deserialize_request(response, response_type):
    """Deserializes response into an object.

    :param response: RESTResponse object to be deserialized.
    :param response_type: class literal for
        deserialized object, or string of class name.

    :return: deserialized object.
    """
    # handle file downloading
    # save response body into a tmp file and return the instance
    if response_type == "file":
        return __deserialize_file(response)
    elif response_type == 'string':
        try:
            data = json.loads(response)
        except ValueError:
            data = response
    else:
        data = response

    return __deserialize(data, response_type)


def __deserialize(data, klass):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if type(klass) == str:
        if klass.startswith('list['):
            sub_kls = re.match(r'list\[(.*)\]', klass).group(1)
            return [__deserialize(sub_data, sub_kls)
                    for sub_data in data]

        if klass.startswith('dict('):
            sub_kls = re.match(r'dict\(([^,]*), (.*)\)', klass).group(2)
            return {k: __deserialize(v, sub_kls)
                    for k, v in six.iteritems(data)}

        # convert str to class
        if klass in NATIVE_TYPES_MAPPING:
            klass = NATIVE_TYPES_MAPPING[klass]
        elif klass == 'Object' and type(data) in PRIMITIVE_TYPES:
            klass = type(data)
        else:
            klass = getattr(adh6.entity, klass)

    if klass in PRIMITIVE_TYPES:
        return __deserialize_primitive(data, klass)
    elif klass == object:
        return __deserialize_object(data)
    elif klass == datetime.date:
        return __deserialize_date(data)
    elif klass == datetime.datetime:
        return __deserialize_datetime(data)
    else:
        return __deserialize_model(data, klass)


def __deserialize_file(response):
    """Deserializes body to file

    Saves response body into a file in a temporary folder,
    using the filename from the `Content-Disposition` header if provided.

    :param response:  RESTResponse.
    :return: file path.
    """
    fd, path = tempfile.mkstemp(dir="/tmp/TODO")
    os.close(fd)
    os.remove(path)

    content_disposition = response.getheader("Content-Disposition")
    if content_disposition:
        filename = re.search(r'filename=[\'"]?([^\'"\s]+)[\'"]?',
                             content_disposition).group(1)
        path = os.path.join(os.path.dirname(path), filename)

    with open(path, "wb") as f:
        f.write(response.data)

    return path


def __deserialize_primitive(data, klass):
    """Deserializes string to primitive type.

    :param data: str.
    :param klass: class literal.

    :return: int, long, float, str, bool.
    """
    try:
        return klass(data)
    except UnicodeEncodeError:
        return six.text_type(data)
    except TypeError:
        return data


def __deserialize_object(value):
    """Return a original value.

    :return: object.
    """
    return value


def __deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :return: date.
    """
    try:
        from dateutil.parser import parse
        return parse(string).date()
    except ImportError:
        return string
    except ValueError:
        raise ValidationError(
            "Failed to parse `{0}` as date object".format(string)
        )


def __deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :return: datetime.
    """
    try:
        from dateutil.parser import parse
        return parse(string)
    except ImportError:
        return string
    except ValueError:
        raise ValidationError(
            "Failed to parse `{0}` as datetime object".format(string)
        )


def __hasattr(object, name):
    return name in object.__class__.__dict__


def __deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :param klass: class literal.
    :return: model object.
    """

    if not klass.swagger_types and not __hasattr(klass, 'get_real_child_model'):
        return data

    kwargs = {}
    if klass.swagger_types is not None:
        for attr, attr_type in six.iteritems(klass.swagger_types):
            if (data is not None and
                    klass.attribute_map[attr] in data and
                    isinstance(data, (list, dict))):
                value = data[klass.attribute_map[attr]]
                kwargs[attr] = __deserialize(value, attr_type)

    instance = klass(**kwargs)

    if (isinstance(instance, dict) and
            klass.swagger_types is not None and
            isinstance(data, dict)):
        for key, value in data.items():
            if key not in klass.swagger_types:
                instance[key] = value
    if __hasattr(instance, 'get_real_child_model'):
        klass_name = instance.get_real_child_model(data)
        if klass_name:
            instance = __deserialize(data, klass_name)

    return instance
