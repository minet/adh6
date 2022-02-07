import os
from dotenv import load_dotenv
load_dotenv("config/.env")

class BaseConfig(object):
    DEBUG = True
    TESTING = True

    # SQLAlchemy configuration variables
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'isolation_level': 'SERIALIZABLE',
        'echo': False,
        'pool_pre_ping': True
    }
    DATABASE = {
        'drivername': 'sqlite',
        'database': ':memory:',
    }
    SESSION_TYPE = 'memcached'
    SECRET_KEY = 'TODO A CHANGER' #@TODO

    # IPs and ports for Elasticsearch nodes
    ELK_HOSTS = [
        {'host': '192.168.102.229', 'port': 9200},
        {'host': '192.168.102.231', 'port': 9200},
        {'host': '192.168.102.227', 'port': 9200},
        {'host': '192.168.102.228', 'port': 9200},
    ]


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True

    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True


class DeployedConfig(BaseConfig):
    GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")
    AUTH_PROFILE_ADDRESS = '{}/profile'.format(os.environ.get("OAUTH2_BASE_PATH"))

    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://{}:{}@{}/{}".format(
        os.environ.get("DATABASE_USERNAME"),
        os.environ.get("DATABASE_PASSWORD"),
        os.environ.get("DATABASE_HOST"),
        os.environ.get("DATABASE_DB_NAME")
    )
    DATABASE = {
        'drivername': 'mysql+mysqldb',
        'host': os.environ.get('DATABASE_HOST'),
        'port': os.environ.get('DATABASE_PORT'),
        'username': os.environ.get('DATABASE_USERNAME'),
        'password': os.environ.get('DATABASE_PASSWORD'),
        'database': os.environ.get('DATABASE_DB_NAME')
    }


class DevelopmentConfig(DeployedConfig):
    DEBUG = True
    TESTING = True

    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True


class ProductionConfig(DeployedConfig):
    pass
