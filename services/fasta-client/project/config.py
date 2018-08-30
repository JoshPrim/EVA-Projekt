# services/users/project/config.py

import os

class BaseConfig:
    """Base configuration"""
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    MONGO_URL = os.environ.get('MONGO_URL')
    MONGO_TEST_URL = os.environ.get('MONGO_TEST_URL')

    FASTA_URL= os.environ.get('FaSta_URL')
    FASTA_TOKEN = 'd16d67e35458c895f557696799eb4e8f'

    @staticmethod
    def config(name):
      return DevelopmentConfig

class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')

class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')