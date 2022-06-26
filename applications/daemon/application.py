from flask import Flask
from configuration import Configuration
from models import database, Product, Order
from redis import Redis
import json
from applications.models import Category, ProductCategory

application = Flask(__name__)
application.config.from_object(Configuration)

# proverava validnost podataka koji su stigli od warehouse-a

with application.app_context() as context:
    database.init_app(application)
    with Redis(host=Configuration.REDIS_HOST) as redis:

        channel = redis.pubsub()
        channel.subscribe(Configuration.REDIS_MESSAGE_CHANNEL)

        while True:
            message = channel.get_message()
            if message is not None and message['data'] != 1:
                batch = json.loads(message['data'].decode("utf-8"))

                products = []
                for product in batch.get('products'):
                    name = product.get('name')
                    categories_string = product.get('categories')
                    categories = categories_string.split('|')
                    print(categories)  # should be a list of category names
                    delivery_quantity = int(product.get('quantity'))
                    delivery_price = float(product.get('price'))

                    old_product = Product.query.filter(Product.name == name)
                    if old_product is None:
                        new_product = Product(name=name, quantity=delivery_quantity, price=delivery_price)
                        database.session.add(new_product)
                        for c_name in categories:
                            if Category.query.filter(Category.name == c_name) is None:
                                category = Category(name=c_name)
                                database.session.add(category)
                            category_id = Category.query.filter(Category.name == c_name).id
                            product_category = ProductCategory(productId=new_product.id, category_id=category_id)
                            database.session.add(product_category)
                    else:
                        # ako jeste - onda se proverava da li je lista kategorija ista kao u bazi
                            # AKO NE - info o proizvodu se odbacuju kao nekorektne
                            # else - azuriramo kolicinu i cenu proizvoda]

                        old_quantity = old_product.quantity
                        old_price = old_product.price
                        new_price = (old_quantity * old_price + delivery_quantity * delivery_price)\
                                    / (old_quantity + delivery_quantity)

                        product_id = old_product.id
                        database.session.delete(old_product)
                        new_product = Product(id=product_id, name=name, quantity=old_quantity+delivery_quantity, price=new_price)
                        database.session.add(new_product)
                    database.session.commit()
