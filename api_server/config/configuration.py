import os
import re

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

    if os.environ.get("ELK_ENABLED", False):
        # IPs and ports for Elasticsearch nodes
        ELK_HOSTS = [
            {
                'scheme': s.group('scheme'), 
                'host': s.group('host'), 
                'port': int(s.group('port'))
            } 
            for s in [
                re.search(
                    pattern=r'(?P<scheme>https|http):\/\/(?P<host>(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}):(?P<port>\d+)', 
                    string=i
                ) 
                for i in os.environ.get("ELK_HOSTS", "http://localhost:9200,https://locahost:9200").split(",")
            ] 
            if s
        ]
        ELK_USER = os.environ.get("ELK_USER")
        ELK_SECRET = os.environ.get("ELK_SECRET")


class DevelopmentConfig(DeployedConfig):
    pass


class ProductionConfig(DeployedConfig):
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False

