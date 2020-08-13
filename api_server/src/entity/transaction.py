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

from src.entity import AbstractTransaction


class Transaction(object):
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
        'name': 'str',
        'src': 'Object',
        'dst': 'Object',
        'timestamp': 'datetime',
        'payment_method': 'Object',
        'value': 'float',
        'attachments': 'list[str]',
        'author': 'Object',
        'pending_validation': 'bool',
        'cashbox': 'str'
    }
    if hasattr(AbstractTransaction, "swagger_types"):
        swagger_types.update(AbstractTransaction.swagger_types)

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'src': 'src',
        'dst': 'dst',
        'timestamp': 'timestamp',
        'payment_method': 'paymentMethod',
        'value': 'value',
        'attachments': 'attachments',
        'author': 'author',
        'pending_validation': 'pendingValidation',
        'cashbox': 'cashbox'
    }
    if hasattr(AbstractTransaction, "attribute_map"):
        attribute_map.update(AbstractTransaction.attribute_map)

    def __init__(self, id=None, name=None, src=None, dst=None, timestamp=None, payment_method=None, value=None, attachments=None, author=None, pending_validation=None, cashbox=None, *args, **kwargs):  # noqa: E501
        """Transaction - a model defined in Swagger"""  # noqa: E501
        AbstractTransaction.__init__(self, *args, **kwargs)
        self._id = None
        self._name = None
        self._src = None
        self._dst = None
        self._timestamp = None
        self._payment_method = None
        self._value = None
        self._attachments = None
        self._author = None
        self._pending_validation = None
        self._cashbox = None
        self.discriminator = None
        self.id = id
        self.name = name
        self.src = src
        self.dst = dst
        if timestamp is not None:
            self.timestamp = timestamp
        self.payment_method = payment_method
        self.value = value
        if attachments is not None:
            self.attachments = attachments
        if author is not None:
            self.author = author
        if pending_validation is not None:
            self.pending_validation = pending_validation
        if cashbox is not None:
            self.cashbox = cashbox

    @property
    def id(self):
        """Gets the id of this Transaction.  # noqa: E501

        The unique identifier of this transaction  # noqa: E501

        :return: The id of this Transaction.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Transaction.

        The unique identifier of this transaction  # noqa: E501

        :param id: The id of this Transaction.  # noqa: E501
        :type: int
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def name(self):
        """Gets the name of this Transaction.  # noqa: E501

        The description of this transaction  # noqa: E501

        :return: The name of this Transaction.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Transaction.

        The description of this transaction  # noqa: E501

        :param name: The name of this Transaction.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def src(self):
        """Gets the src of this Transaction.  # noqa: E501

        The source account of this transaction  # noqa: E501

        :return: The src of this Transaction.  # noqa: E501
        :rtype: Object
        """
        return self._src

    @src.setter
    def src(self, src):
        """Sets the src of this Transaction.

        The source account of this transaction  # noqa: E501

        :param src: The src of this Transaction.  # noqa: E501
        :type: Object
        """
        if src is None:
            raise ValueError("Invalid value for `src`, must not be `None`")  # noqa: E501

        self._src = src

    @property
    def dst(self):
        """Gets the dst of this Transaction.  # noqa: E501

        The destination account of this transaction  # noqa: E501

        :return: The dst of this Transaction.  # noqa: E501
        :rtype: Object
        """
        return self._dst

    @dst.setter
    def dst(self, dst):
        """Sets the dst of this Transaction.

        The destination account of this transaction  # noqa: E501

        :param dst: The dst of this Transaction.  # noqa: E501
        :type: Object
        """
        if dst is None:
            raise ValueError("Invalid value for `dst`, must not be `None`")  # noqa: E501

        self._dst = dst

    @property
    def timestamp(self):
        """Gets the timestamp of this Transaction.  # noqa: E501

        The date-time at which this transaction was executed  # noqa: E501

        :return: The timestamp of this Transaction.  # noqa: E501
        :rtype: datetime
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this Transaction.

        The date-time at which this transaction was executed  # noqa: E501

        :param timestamp: The timestamp of this Transaction.  # noqa: E501
        :type: datetime
        """

        self._timestamp = timestamp

    @property
    def payment_method(self):
        """Gets the payment_method of this Transaction.  # noqa: E501

        The payment method used for this transaction  # noqa: E501

        :return: The payment_method of this Transaction.  # noqa: E501
        :rtype: Object
        """
        return self._payment_method

    @payment_method.setter
    def payment_method(self, payment_method):
        """Sets the payment_method of this Transaction.

        The payment method used for this transaction  # noqa: E501

        :param payment_method: The payment_method of this Transaction.  # noqa: E501
        :type: Object
        """
        if payment_method is None:
            raise ValueError("Invalid value for `payment_method`, must not be `None`")  # noqa: E501

        self._payment_method = payment_method

    @property
    def value(self):
        """Gets the value of this Transaction.  # noqa: E501

        The unsigned value of this transaction  # noqa: E501

        :return: The value of this Transaction.  # noqa: E501
        :rtype: float
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this Transaction.

        The unsigned value of this transaction  # noqa: E501

        :param value: The value of this Transaction.  # noqa: E501
        :type: float
        """
        if value is None:
            raise ValueError("Invalid value for `value`, must not be `None`")  # noqa: E501

        self._value = value

    @property
    def attachments(self):
        """Gets the attachments of this Transaction.  # noqa: E501

        The list of attachments linked with this transaction  # noqa: E501

        :return: The attachments of this Transaction.  # noqa: E501
        :rtype: list[str]
        """
        return self._attachments

    @attachments.setter
    def attachments(self, attachments):
        """Sets the attachments of this Transaction.

        The list of attachments linked with this transaction  # noqa: E501

        :param attachments: The attachments of this Transaction.  # noqa: E501
        :type: list[str]
        """

        self._attachments = attachments

    @property
    def author(self):
        """Gets the author of this Transaction.  # noqa: E501

        The member who executed this transaction  # noqa: E501

        :return: The author of this Transaction.  # noqa: E501
        :rtype: Object
        """
        return self._author

    @author.setter
    def author(self, author):
        """Sets the author of this Transaction.

        The member who executed this transaction  # noqa: E501

        :param author: The author of this Transaction.  # noqa: E501
        :type: Object
        """

        self._author = author

    @property
    def pending_validation(self):
        """Gets the pending_validation of this Transaction.  # noqa: E501

        Whether this transaction is awaiting confirmation from a member with higher privileges  # noqa: E501

        :return: The pending_validation of this Transaction.  # noqa: E501
        :rtype: bool
        """
        return self._pending_validation

    @pending_validation.setter
    def pending_validation(self, pending_validation):
        """Sets the pending_validation of this Transaction.

        Whether this transaction is awaiting confirmation from a member with higher privileges  # noqa: E501

        :param pending_validation: The pending_validation of this Transaction.  # noqa: E501
        :type: bool
        """

        self._pending_validation = pending_validation

    @property
    def cashbox(self):
        """Gets the cashbox of this Transaction.  # noqa: E501

        Whether to use the cashbox or not  # noqa: E501

        :return: The cashbox of this Transaction.  # noqa: E501
        :rtype: str
        """
        return self._cashbox

    @cashbox.setter
    def cashbox(self, cashbox):
        """Sets the cashbox of this Transaction.

        Whether to use the cashbox or not  # noqa: E501

        :param cashbox: The cashbox of this Transaction.  # noqa: E501
        :type: str
        """

        self._cashbox = cashbox

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
        if issubclass(Transaction, dict):
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
        if not isinstance(other, Transaction):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
