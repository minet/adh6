from enum import Enum


class Roles(Enum):
    USER = "user"
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_PROD = "admin:prod"
    TRESO_READ = "treasurer:read"
    TRESO_WRITE = "treasurer:write"
    NETWORK_READ = "network:read"
    NETWORK_WRITE = "network:write"
    NETWORK_PROD = "network:write:prod"
    NETWORK_DEV = "network:write:dev"
    NETWORK_HOSTING = "network:write:hosting"


class AuthenticationMethod(Enum):
    NONE = "none"
    API_KEY = "api_key"
    OIDC = "oidc"
    USER = "user"
