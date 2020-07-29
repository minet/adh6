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

from src.entity import AbstractAccount


class Account(object):
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
        'actif': 'bool',
        'pinned': 'bool',
        'compte_courant': 'bool',
        'account_type': 'Object',
        'creation_date': 'datetime',
        'member': 'Object',
        'name': 'str',
        'id': 'int',
        'balance': 'float',
        'pending_balance': 'float'
    }
    if hasattr(AbstractAccount, "swagger_types"):
        swagger_types.update(AbstractAccount.swagger_types)

    attribute_map = {
        'actif': 'actif',
        'pinned': 'pinned',
        'compte_courant': 'compteCourant',
        'account_type': 'accountType',
        'creation_date': 'creationDate',
        'member': 'member',
        'name': 'name',
        'id': 'id',
        'balance': 'balance',
        'pending_balance': 'pendingBalance'
    }
    if hasattr(AbstractAccount, "attribute_map"):
        attribute_map.update(AbstractAccount.attribute_map)

    def __init__(self, actif=True, pinned=False, compte_courant=False, account_type=None, creation_date=None, member=None, name=None, id=None, balance=None, pending_balance=None, *args, **kwargs):  # noqa: E501
        """Account - a model defined in Swagger"""  # noqa: E501
        AbstractAccount.__init__(self, *args, **kwargs)
        self._actif = None
        self._pinned = None
        self._compte_courant = None
        self._account_type = None
        self._creation_date = None
        self._member = None
        self._name = None
        self._id = None
        self._balance = None
        self._pending_balance = None
        self.discriminator = None
        if actif is not None:
            self.actif = actif
        if pinned is not None:
            self.pinned = pinned
        if compte_courant is not None:
            self.compte_courant = compte_courant
        self.account_type = account_type
        if creation_date is not None:
            self.creation_date = creation_date
        if member is not None:
            self.member = member
        self.name = name
        self.id = id
        self.balance = balance
        self.pending_balance = pending_balance

    @property
    def actif(self):
        """Gets the actif of this Account.  # noqa: E501

        Whether this account is active or not  # noqa: E501

        :return: The actif of this Account.  # noqa: E501
        :rtype: bool
        """
        return self._actif

    @actif.setter
    def actif(self, actif):
        """Sets the actif of this Account.

        Whether this account is active or not  # noqa: E501

        :param actif: The actif of this Account.  # noqa: E501
        :type: bool
        """

        self._actif = actif

    @property
    def pinned(self):
        """Gets the pinned of this Account.  # noqa: E501

        Whether this account should be displayed before others  # noqa: E501

        :return: The pinned of this Account.  # noqa: E501
        :rtype: bool
        """
        return self._pinned

    @pinned.setter
    def pinned(self, pinned):
        """Sets the pinned of this Account.

        Whether this account should be displayed before others  # noqa: E501

        :param pinned: The pinned of this Account.  # noqa: E501
        :type: bool
        """

        self._pinned = pinned

    @property
    def compte_courant(self):
        """Gets the compte_courant of this Account.  # noqa: E501

        Whether this account depends on MiNET's main account  # noqa: E501

        :return: The compte_courant of this Account.  # noqa: E501
        :rtype: bool
        """
        return self._compte_courant

    @compte_courant.setter
    def compte_courant(self, compte_courant):
        """Sets the compte_courant of this Account.

        Whether this account depends on MiNET's main account  # noqa: E501

        :param compte_courant: The compte_courant of this Account.  # noqa: E501
        :type: bool
        """

        self._compte_courant = compte_courant

    @property
    def account_type(self):
        """Gets the account_type of this Account.  # noqa: E501

        The type of this account  # noqa: E501

        :return: The account_type of this Account.  # noqa: E501
        :rtype: Object
        """
        return self._account_type

    @account_type.setter
    def account_type(self, account_type):
        """Sets the account_type of this Account.

        The type of this account  # noqa: E501

        :param account_type: The account_type of this Account.  # noqa: E501
        :type: Object
        """
        if account_type is None:
            raise ValueError("Invalid value for `account_type`, must not be `None`")  # noqa: E501

        self._account_type = account_type

    @property
    def creation_date(self):
        """Gets the creation_date of this Account.  # noqa: E501

        The date-time at which this account was first created  # noqa: E501

        :return: The creation_date of this Account.  # noqa: E501
        :rtype: datetime
        """
        return self._creation_date

    @creation_date.setter
    def creation_date(self, creation_date):
        """Sets the creation_date of this Account.

        The date-time at which this account was first created  # noqa: E501

        :param creation_date: The creation_date of this Account.  # noqa: E501
        :type: datetime
        """

        self._creation_date = creation_date

    @property
    def member(self):
        """Gets the member of this Account.  # noqa: E501

        The member this account belongs to  # noqa: E501

        :return: The member of this Account.  # noqa: E501
        :rtype: Object
        """
        return self._member

    @member.setter
    def member(self, member):
        """Sets the member of this Account.

        The member this account belongs to  # noqa: E501

        :param member: The member of this Account.  # noqa: E501
        :type: Object
        """

        self._member = member

    @property
    def name(self):
        """Gets the name of this Account.  # noqa: E501

        The name of this account  # noqa: E501

        :return: The name of this Account.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Account.

        The name of this account  # noqa: E501

        :param name: The name of this Account.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def id(self):
        """Gets the id of this Account.  # noqa: E501

        The unique identifier of this account  # noqa: E501

        :return: The id of this Account.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Account.

        The unique identifier of this account  # noqa: E501

        :param id: The id of this Account.  # noqa: E501
        :type: int
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def balance(self):
        """Gets the balance of this Account.  # noqa: E501

        The current balance of this account  # noqa: E501

        :return: The balance of this Account.  # noqa: E501
        :rtype: float
        """
        return self._balance

    @balance.setter
    def balance(self, balance):
        """Sets the balance of this Account.

        The current balance of this account  # noqa: E501

        :param balance: The balance of this Account.  # noqa: E501
        :type: float
        """
        if balance is None:
            raise ValueError("Invalid value for `balance`, must not be `None`")  # noqa: E501

        self._balance = balance

    @property
    def pending_balance(self):
        """Gets the pending_balance of this Account.  # noqa: E501

        The pending balance of this account  # noqa: E501

        :return: The pending_balance of this Account.  # noqa: E501
        :rtype: float
        """
        return self._pending_balance

    @pending_balance.setter
    def pending_balance(self, pending_balance):
        """Sets the pending_balance of this Account.

        The pending balance of this account  # noqa: E501

        :param pending_balance: The pending_balance of this Account.  # noqa: E501
        :type: float
        """
        if pending_balance is None:
            raise ValueError("Invalid value for `pending_balance`, must not be `None`")  # noqa: E501

        self._pending_balance = pending_balance

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
        if issubclass(Account, dict):
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
        if not isinstance(other, Account):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
