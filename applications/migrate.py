from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database
from sqlalchemy_utils import database_exists, drop_database, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObjects = Migrate(application, database)

migrationSuccessful = False

while not migrationSuccessful:
    try:
        if database_exists(application.config['SQLALCHEMY_DATABASE_URI']):
            drop_database(application.config['SQLALCHEMY_DATABASE_URI'])
        if not database_exists(application.config['SQLALCHEMY_DATABASE_URI']):
            create_database(application.config['SQLALCHEMY_DATABASE_URI'])

        database.init_app(application)

        with application.app_context() as context:
            init()
            migrate(message='Production migration')
            upgrade()
            migrationSuccessful = True

    except Exception as err:
        print(err)
