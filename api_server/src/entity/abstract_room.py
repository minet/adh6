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


class AbstractRoom(object):
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

    attribute_map = {
        'id': 'id',
        'description': 'description',
        'room_number': 'roomNumber',
        'vlan': 'vlan'
    }

    def __init__(self, id=None, description=None, room_number=None, vlan=None):  # noqa: E501
        """AbstractRoom - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._description = None
        self._room_number = None
        self._vlan = None
        self.discriminator = None
        if id is not None:
            self.id = id
        if description is not None:
            self.description = description
        if room_number is not None:
            self.room_number = room_number
        if vlan is not None:
            self.vlan = vlan

    @property
    def id(self):
        """Gets the id of this AbstractRoom.  # noqa: E501

        The unique identifier of this room  # noqa: E501

        :return: The id of this AbstractRoom.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this AbstractRoom.

        The unique identifier of this room  # noqa: E501

        :param id: The id of this AbstractRoom.  # noqa: E501
        :type: int
        """

        self._id = id

    @property
    def description(self):
        """Gets the description of this AbstractRoom.  # noqa: E501

        The friendly description of this room  # noqa: E501

        :return: The description of this AbstractRoom.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this AbstractRoom.

        The friendly description of this room  # noqa: E501

        :param description: The description of this AbstractRoom.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def room_number(self):
        """Gets the room_number of this AbstractRoom.  # noqa: E501

        The room number according to the Maisel  # noqa: E501

        :return: The room_number of this AbstractRoom.  # noqa: E501
        :rtype: int
        """
        return self._room_number

    @room_number.setter
    def room_number(self, room_number):
        """Sets the room_number of this AbstractRoom.

        The room number according to the Maisel  # noqa: E501

        :param room_number: The room_number of this AbstractRoom.  # noqa: E501
        :type: int
        """

        self._room_number = room_number

    @property
    def vlan(self):
        """Gets the vlan of this AbstractRoom.  # noqa: E501

        The main vlan assigned to this room  # noqa: E501

        :return: The vlan of this AbstractRoom.  # noqa: E501
        :rtype: int
        """
        return self._vlan

    @vlan.setter
    def vlan(self, vlan):
        """Sets the vlan of this AbstractRoom.

        The main vlan assigned to this room  # noqa: E501

        :param vlan: The vlan of this AbstractRoom.  # noqa: E501
        :type: int
        """

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
        if issubclass(AbstractRoom, dict):
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
        if not isinstance(other, AbstractRoom):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other