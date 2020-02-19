# coding=utf-8
import datetime
import decimal

import six

from src.entity.null import Null

PRIMITIVE_TYPES = (float, bool, bytes, six.text_type, decimal.Decimal) + six.integer_types


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
    elif isinstance(obj, Null):
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

    return {key: serialize_response(val)
            for key, val in six.iteritems(obj_dict)}