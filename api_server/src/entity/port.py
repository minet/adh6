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

from src.entity import AbstractPort


class Port(object):
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
        'port_number': 'str',
        'oid': 'str',
        'room': 'Object',
        'switch_obj': 'Object'
    }
    if hasattr(AbstractPort, "swagger_types"):
        swagger_types.update(AbstractPort.swagger_types)

    attribute_map = {
        'id': 'id',
        'port_number': 'portNumber',
        'oid': 'oid',
        'room': 'room',
        'switch_obj': 'switchObj'
    }
    if hasattr(AbstractPort, "attribute_map"):
        attribute_map.update(AbstractPort.attribute_map)

    def __init__(self, id=None, port_number=None, oid=None, room=None, switch_obj=None, *args, **kwargs):  # noqa: E501
        """Port - a model defined in Swagger"""  # noqa: E501
        AbstractPort.__init__(self, *args, **kwargs)
        self._id = None
        self._port_number = None
        self._oid = None
        self._room = None
        self._switch_obj = None
        self.discriminator = None
        self.id = id
        self.port_number = port_number
        self.oid = oid
        self.room = room
        self.switch_obj = switch_obj

    @property
    def id(self):
        """Gets the id of this Port.  # noqa: E501

        The unique identifier of this port  # noqa: E501

        :return: The id of this Port.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Port.

        The unique identifier of this port  # noqa: E501

        :param id: The id of this Port.  # noqa: E501
        :type: int
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def port_number(self):
        """Gets the port_number of this Port.  # noqa: E501

        The friendly (Cisco) number of this port  # noqa: E501

        :return: The port_number of this Port.  # noqa: E501
        :rtype: str
        """
        return self._port_number

    @port_number.setter
    def port_number(self, port_number):
        """Sets the port_number of this Port.

        The friendly (Cisco) number of this port  # noqa: E501

        :param port_number: The port_number of this Port.  # noqa: E501
        :type: str
        """
        if port_number is None:
            raise ValueError("Invalid value for `port_number`, must not be `None`")  # noqa: E501

        self._port_number = port_number

    @property
    def oid(self):
        """Gets the oid of this Port.  # noqa: E501

        The oid of this port for SNMP access  # noqa: E501

        :return: The oid of this Port.  # noqa: E501
        :rtype: str
        """
        return self._oid

    @oid.setter
    def oid(self, oid):
        """Sets the oid of this Port.

        The oid of this port for SNMP access  # noqa: E501

        :param oid: The oid of this Port.  # noqa: E501
        :type: str
        """
        if oid is None:
            raise ValueError("Invalid value for `oid`, must not be `None`")  # noqa: E501

        self._oid = oid

    @property
    def room(self):
        """Gets the room of this Port.  # noqa: E501

        The room this port is in  # noqa: E501

        :return: The room of this Port.  # noqa: E501
        :rtype: Object
        """
        return self._room

    @room.setter
    def room(self, room):
        """Sets the room of this Port.

        The room this port is in  # noqa: E501

        :param room: The room of this Port.  # noqa: E501
        :type: Object
        """
        if room is None:
            raise ValueError("Invalid value for `room`, must not be `None`")  # noqa: E501

        self._room = room

    @property
    def switch_obj(self):
        """Gets the switch_obj of this Port.  # noqa: E501

        The switch this port is a member of  # noqa: E501

        :return: The switch_obj of this Port.  # noqa: E501
        :rtype: Object
        """
        return self._switch_obj

    @switch_obj.setter
    def switch_obj(self, switch_obj):
        """Sets the switch_obj of this Port.

        The switch this port is a member of  # noqa: E501

        :param switch_obj: The switch_obj of this Port.  # noqa: E501
        :type: Object
        """
        if switch_obj is None:
            raise ValueError("Invalid value for `switch_obj`, must not be `None`")  # noqa: E501

        self._switch_obj = switch_obj

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
        if issubclass(Port, dict):
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
        if not isinstance(other, Port):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
