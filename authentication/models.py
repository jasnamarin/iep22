from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class UserRole(database.Model):
    __tablename__ = 'user_role'

    id = database.Column(database.Integer, primary_key=True)
    userId = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    roleId = database.Column(database.Integer, database.ForeignKey('role.id'), nullable=False)


class User (database.Model):
    __tablename__ = 'user'

    id = database.Column(database.Integer, primary_key=True)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)

    roles = database.relationship('Role', secondary=UserRole.__table__, back_populates='users')

    def __repr__(self):
        return str(dict(forename=self.forename, surname=self.surname, jmbg=self.jmbg, email=self.email))


class Role (database.Model):
    __tablename__ = 'role'

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    users = database.relationship('User', secondary=UserRole.__table__, back_populates='roles')
