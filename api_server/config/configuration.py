import os

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
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # IPs and ports for Elasticsearch nodes
    ELK_HOSTS = [
        {'scheme': 'http', 'host': '192.168.102.229', 'port': 9200},
        {'scheme': 'http', 'host': '192.168.102.231', 'port': 9200},
        {'scheme': 'http', 'host': '192.168.102.227', 'port': 9200},
        {'scheme': 'http', 'host': '192.168.102.228', 'port': 9200},
    ]


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True

    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True


class DeployedConfig(BaseConfig):
    DEBUG = False
    TESTING = False

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
    pass


class ProductionConfig(DeployedConfig):
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False

