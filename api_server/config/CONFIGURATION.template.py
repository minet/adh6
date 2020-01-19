API_CONF = {
    'AUTH_SERVER_ADDRESS': '${CAS_PROFILE_URL}',
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


