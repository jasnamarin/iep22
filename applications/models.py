from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = 'product_category'
    id = database.Column(database.Integer, primary_key=True)

    productId = database.Column(database.Integer, database.ForeignKey('product.id'), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey('category.id'), nullable=False)


class Category(database.Model):
    __tablename__ = 'category'
    id = database.Column(database.Integer, primary_key=True)

    name = database.Column(database.String(256), nullable=False)

    products = database.relationship('Product', secondary=ProductCategory.__table__,
                                     back_populates='categories')


class Product(database.Model):
    __tablename__ = 'product'
    id = database.Column(database.Integer, primary_key=True)

    name = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float)
    quantity = database.Column(database.Integer)

    categories = database.relationship('Category', secondary=ProductCategory.__table__,
                                       back_populates='products')


class Order(database.Model):
    __tablename__ = 'order'
    id = database.Column(database.Integer, primary_key=True)

    total_price = database.Column(database.Float)
    status = database.Column(database.Boolean)
    timestamp = database.Column(database.String(256))

    products = database.relationship('Product')
