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


class MembershipRequest(object):
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
        'duration': 'int',
        'payment_method': 'OneOfMembershipRequestPaymentMethod',
        'first_time': 'bool'
    }

    attribute_map = {
        'duration': 'duration',
        'payment_method': 'paymentMethod',
        'first_time': 'firstTime'
    }

    def __init__(self, duration=None, payment_method=None, first_time=None):  # noqa: E501
        """MembershipRequest - a model defined in Swagger"""  # noqa: E501
        self._duration = None
        self._payment_method = None
        self._first_time = None
        self.discriminator = None
        self.duration = duration
        self.payment_method = payment_method
        self.first_time = first_time

    @property
    def duration(self):
        """Gets the duration of this MembershipRequest.  # noqa: E501

        The duration in days this membership is for  # noqa: E501

        :return: The duration of this MembershipRequest.  # noqa: E501
        :rtype: int
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        """Sets the duration of this MembershipRequest.

        The duration in days this membership is for  # noqa: E501

        :param duration: The duration of this MembershipRequest.  # noqa: E501
        :type: int
        """
        if duration is None:
            raise ValueError("Invalid value for `duration`, must not be `None`")  # noqa: E501

        self._duration = duration

    @property
    def payment_method(self):
        """Gets the payment_method of this MembershipRequest.  # noqa: E501

        The payment method used to pay the membership fee  # noqa: E501

        :return: The payment_method of this MembershipRequest.  # noqa: E501
        :rtype: OneOfMembershipRequestPaymentMethod
        """
        return self._payment_method

    @payment_method.setter
    def payment_method(self, payment_method):
        """Sets the payment_method of this MembershipRequest.

        The payment method used to pay the membership fee  # noqa: E501

        :param payment_method: The payment_method of this MembershipRequest.  # noqa: E501
        :type: OneOfMembershipRequestPaymentMethod
        """
        if payment_method is None:
            raise ValueError("Invalid value for `payment_method`, must not be `None`")  # noqa: E501

        self._payment_method = payment_method

    @property
    def first_time(self):
        """Gets the first_time of this MembershipRequest.  # noqa: E501

        Whether or not this membership request is the member's first  # noqa: E501

        :return: The first_time of this MembershipRequest.  # noqa: E501
        :rtype: bool
        """
        return self._first_time

    @first_time.setter
    def first_time(self, first_time):
        """Sets the first_time of this MembershipRequest.

        Whether or not this membership request is the member's first  # noqa: E501

        :param first_time: The first_time of this MembershipRequest.  # noqa: E501
        :type: bool
        """
        if first_time is None:
            raise ValueError("Invalid value for `first_time`, must not be `None`")  # noqa: E501

        self._first_time = first_time

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
        if issubclass(MembershipRequest, dict):
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
        if not isinstance(other, MembershipRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
