# coding: utf-8

"""
    ADH6 API

    This is the specification for **MiNET**'s ADH6 plaform. Its aim is to manage our users, devices and treasury.   # noqa: E501

    OpenAPI spec version: 2.0.0
    Contact: equipe@minet.net
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

from src.entity.decorator.entity_property import entity_property

from src.entity import AbstractRoom


class Room(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'id': 'int',
        'description': 'str',
        'room_number': 'int',
        'vlan': 'int'
    }
    if hasattr(AbstractRoom, "swagger_types"):
        swagger_types.update(AbstractRoom.swagger_types)

    attribute_map = {
        'id': 'id',
        'description': 'description',
        'room_number': 'roomNumber',
        'vlan': 'vlan'
    }
    if hasattr(AbstractRoom, "attribute_map"):
        attribute_map.update(AbstractRoom.attribute_map)

    def __init__(self, id=None, description=None, room_number=None, vlan=None, *args, **kwargs):  # noqa: E501
        """Room - a model defined in Swagger"""  # noqa: E501
        AbstractRoom.__init__(self, *args, **kwargs)
        self._id = None
        self._description = None
        self._room_number = None
        self._vlan = None
        self.discriminator = None
        self.id = id
        self.description = description
        self.room_number = room_number
        self.vlan = vlan

    @entity_property
    def id(self):
        """Gets the id of this Room.  # noqa: E501

        The unique identifier of this room  # noqa: E501

        :return: The id of this Room.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Room.

        The unique identifier of this room  # noqa: E501

        :param id: The id of this Room.  # noqa: E501
        :type: int
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @entity_property
    def description(self):
        """Gets the description of this Room.  # noqa: E501

        The friendly description of this room  # noqa: E501

        :return: The description of this Room.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Room.

        The friendly description of this room  # noqa: E501

        :param description: The description of this Room.  # noqa: E501
        :type: str
        """
        if description is None:
            raise ValueError("Invalid value for `description`, must not be `None`")  # noqa: E501

        self._description = description

    @entity_property
    def room_number(self):
        """Gets the room_number of this Room.  # noqa: E501

        The room number according to the Maisel  # noqa: E501

        :return: The room_number of this Room.  # noqa: E501
        :rtype: int
        """
        return self._room_number

    @room_number.setter
    def room_number(self, room_number):
        """Sets the room_number of this Room.

        The room number according to the Maisel  # noqa: E501

        :param room_number: The room_number of this Room.  # noqa: E501
        :type: int
        """
        if room_number is None:
            raise ValueError("Invalid value for `room_number`, must not be `None`")  # noqa: E501

        self._room_number = room_number

    @entity_property
    def vlan(self):
        """Gets the vlan of this Room.  # noqa: E501

        The main vlan assigned to this room  # noqa: E501

        :return: The vlan of this Room.  # noqa: E501
        :rtype: int
        """
        return self._vlan

    @vlan.setter
    def vlan(self, vlan):
        """Sets the vlan of this Room.

        The main vlan assigned to this room  # noqa: E501

        :param vlan: The vlan of this Room.  # noqa: E501
        :type: int
        """
        if vlan is None:
            raise ValueError("Invalid value for `vlan`, must not be `None`")  # noqa: E501

        self._vlan = vlan

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(Room, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Room):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
