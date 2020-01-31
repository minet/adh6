OAUTH2_SCOPES = {
  'openid': {
    'name': 'openid',
    'description': 'Accès élémentaire aux informations suivantes',
    'mandatory': True,
    'hidden': True
  },
  'profile': {
    'name': 'profile',
    'description': 'Accès aux informations de base du profil: nom, prénom etc',
    'mandatory': True,
    'hidden': False
  },
  'offline_access': {
    'name': 'offline_access',
    'description': 'Autorise l\'application à s\'authentifier automatiquement',
    'mandatory': False,
    'hidden': False
  },
  'roles': {
    'name': 'roles',
    'description': 'Accès à la liste des roles pour la gestion des permissions',
    'mandatory': False,
    'hidden': False
  },
  'account:read': {
    'name': 'account:read',
    'description': 'Accès à la liste des comptes en trésorerie',
    'mandatory': False,
    'hidden': False
  }
}

API_CONF = {
    'AUTH_PROFILE_ADDRESS': '${OAUTH2_BASE_PATH}/profile',
    'AUTH_AUTHORIZE_ADDRESS': '${OAUTH2_BASE_PATH}/authorize',
    'AUTH_CONSENT_ADDRESS': '${AUTH_CONSENT_ADDRESS}',
    'AUTH_METADATA': {
        "issuer": "${OAUTH2_BASE_PATH}",
        "scopes_supported": list(OAUTH2_SCOPES.keys()),
        "response_types_supported": ["token", ],
        "subject_types_supported": ["public"],
        "claim_types_supported": ["normal"],
        "claims_supported": ["sub", "name", "preferred_username", "family_name", "given_name", "middle_name",
                             "given_name", "profile", "picture", "nickname", "website", "zoneinfo", "locale",
                             "updated_at", "birthdate", "email", "email_verified", "phone_number",
                             "phone_number_verified", "address", "gender"],
        "grant_types_supported": ["refresh_token"],
        "id_token_signing_alg_values_supported": ["none"],
        "introspection_endpoint_auth_methods_supported": ["client_secret_basic"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
        "authorization_endpoint": "${OAUTH2_BASE_PATH}/authorize",
        "token_endpoint": "${OAUTH2_BASE_PATH}/token",
        "userinfo_endpoint": "${OAUTH2_BASE_PATH}/profile"
    }
}

GITLAB_CONF = {
    'access_token': '${GITLAB_ACCESS_TOKEN}',
}

DATABASE = {
    'drivername': 'mysql+mysqldb',
    'host': '${DATABASE_HOST}',
    'port': '${DATABASE_PORT}',
    'username': '${DATABASE_USERNAME}',
    'password': '${DATABASE_PASSWORD}',
    'database': '${DATABASE_DB_NAME}'
}

PRICES = {
    31: 9,
    2 * 31: 18,
    3 * 31: 27,
    4 * 31: 36,
    5 * 31: 45,
    360: 50,
}

DURATION_STRING = {
    1: '1 jour',
    360: '1 an',
}

# IPs and ports for Elasticsearch nodes
ELK_HOSTS = [
    {'host': '192.168.102.229', 'port': 9200},
    {'host': '192.168.102.231', 'port': 9200},
    {'host': '192.168.102.227', 'port': 9200},
    {'host': '192.168.102.228', 'port': 9200},
]
