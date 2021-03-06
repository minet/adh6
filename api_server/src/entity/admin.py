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

from src.entity.decorator.entity_property import entity_property as property


class Admin(object):
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
        'login': 'str',
        'member': 'OneOfAdminMember',
        'roles': 'list[str]'
    }

    attribute_map = {
        'login': 'login',
        'member': 'member',
        'roles': 'roles'
    }

    def __init__(self, login=None, member=None, roles=None):  # noqa: E501
        """Admin - a model defined in Swagger"""  # noqa: E501
        self._login = None
        self._member = None
        self._roles = None
        self.discriminator = None
        self.login = login
        if member is not None:
            self.member = member
        self.roles = roles

    @property
    def login(self):
        """Gets the login of this Admin.  # noqa: E501

        The login of this administrator  # noqa: E501

        :return: The login of this Admin.  # noqa: E501
        :rtype: str
        """
        return self._login

    @login.setter
    def login(self, login):
        """Sets the login of this Admin.

        The login of this administrator  # noqa: E501

        :param login: The login of this Admin.  # noqa: E501
        :type: str
        """
        if login is None:
            raise ValueError("Invalid value for `login`, must not be `None`")  # noqa: E501

        self._login = login

    @property
    def member(self):
        """Gets the member of this Admin.  # noqa: E501

        The member associated with this admin  # noqa: E501

        :return: The member of this Admin.  # noqa: E501
        :rtype: OneOfAdminMember
        """
        return self._member

    @member.setter
    def member(self, member):
        """Sets the member of this Admin.

        The member associated with this admin  # noqa: E501

        :param member: The member of this Admin.  # noqa: E501
        :type: OneOfAdminMember
        """

        self._member = member

    @property
    def roles(self):
        """Gets the roles of this Admin.  # noqa: E501

        The list of roles of this administrator  # noqa: E501

        :return: The roles of this Admin.  # noqa: E501
        :rtype: list[str]
        """
        return self._roles

    @roles.setter
    def roles(self, roles):
        """Sets the roles of this Admin.

        The list of roles of this administrator  # noqa: E501

        :param roles: The roles of this Admin.  # noqa: E501
        :type: list[str]
        """
        if roles is None:
            raise ValueError("Invalid value for `roles`, must not be `None`")  # noqa: E501

        self._roles = roles

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
        if issubclass(Admin, dict):
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
        if not isinstance(other, Admin):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
