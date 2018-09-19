import os
from project import app, db

class BaseConfig:
    """Base configuration"""
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRES_URL')
    MASTER_STATION = os.environ.get('MASTER_STATION')
    MASTER_ELEVATOR = os.environ.get('MASTER_ELEVATOR')


    MONGO_URI = os.environ.get('MONGO_URI')
    print(MONGO_URI)
    MONGO_DBNAME = 'eva_dev'

class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')