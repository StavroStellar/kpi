# app/config.py

import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PF*&#R$BDsdfb&#Q4'

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Пожалуйста, войдите, чтобы получить доступ к этой странице.'
    LOGIN_MESSAGE_CATEGORY = 'info'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(Config.BASE_DIR, "database_dev.db")}'


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}