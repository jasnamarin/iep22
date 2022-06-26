from datetime import timedelta
import os

try:
    databaseUrl = os.environ['DATABASE_URL']
except KeyError:
    databaseUrl = 'storeDB'


class Configuration:
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:root@{databaseUrl}/store'
    try:
        REDIS_HOST = os.environ['REDIS_URI']
    except KeyError:
        REDIS_HOST = 'localhost'
#    REDIS_PRODUCTS_LIST = 'products'
    REDIS_MESSAGE_CHANNEL = 'notification'
    JWT_SECRET_KEY = 'JWT_SECRET_KEY'
    JSON_SORT_KEYS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
