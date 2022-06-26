from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, User, UserRole
from sqlalchemy_utils import database_exists, create_database, drop_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

migrationSuccessful = False

while not migrationSuccessful:
    try:
        if database_exists(application.config['SQLALCHEMY_DATABASE_URI']):
            drop_database(application.config['SQLALCHEMY_DATABASE_URI'])  # delete later...
        if not database_exists(application.config['SQLALCHEMY_DATABASE_URI']):
            create_database(application.config['SQLALCHEMY_DATABASE_URI'])

        database.init_app(application)

        with application.app_context() as context:
            init()
            migrate(message='Production migration')
            upgrade()

            adminRole = Role(name='admin')
            warehouseRole = Role(name='warehouse')
            customerRole = Role(name='customer')

            database.session.add(adminRole)
            database.session.add(warehouseRole)
            database.session.add(customerRole)
            database.session.commit()

            admin = User(
                forename='admin',
                surname='admin',
                email='admin@admin.com',
                password='1'
            )

            database.session.add(admin)
            database.session.commit()

            userRole = UserRole(
                userId=admin.id,
                roleId=adminRole.id
            )

            database.session.add(userRole)
            database.session.commit()

            migrationSuccessful = True
    except Exception as err:
        print(err)
