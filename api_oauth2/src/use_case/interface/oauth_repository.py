# coding=utf-8
"""
OAuth repository.
"""
import abc


class OAuthRepository(metaclass=abc.ABCMeta):
    """
    Abstract interface to handle oauth storage.
    """

    @abc.abstractmethod
    def create_client(self, ctx, token_endpoint_auth_method=None, client_id=None):
        """
        Create a new OAuth client.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_client(self, ctx, client_id=None):
        pass

    @abc.abstractmethod
    def delete_client(self, ctx, client_id=None):
        pass

    @abc.abstractmethod
    def create_token(self, ctx, client_id=None, username=None, access_token=None, expires_at=None, scope=None,
                     refresh_token=None):
        pass

    @abc.abstractmethod
    def get_token(self, ctx, access_token=None):
        pass