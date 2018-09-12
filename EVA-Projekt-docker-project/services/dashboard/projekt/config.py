import os

class BaseConfig:
    """Base configuration"""
    TESTING = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    POSTGRES_URL = os.environ.get('POSTGRES_URL')
    MONGO_URI = os.environ.get('MONGO_URI')

    MONGO_DBNAME = 'eva_dev'

class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    POSTGRES_URL = os.environ.get('POSTGRES_URL')
    MONGO_URI = os.environ.get('MONGO_URI')

    MONGO_DBNAME = 'eva_dev'
