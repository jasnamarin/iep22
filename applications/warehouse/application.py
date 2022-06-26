import io
import csv
import json
from flask import Flask, request, jsonify, Response
from configuration import Configuration
from flask_jwt_extended import JWTManager
from redis import Redis
from utils import role_check

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route('/update', methods=['POST'])
@role_check('warehouse')
def update():
    file = request.files.get('file')
    if file is None:
        return jsonify(message='Field file is missing.'), 400

    products = []

    stream = io.StringIO(file.stream.read().decode(encoding="utf8"))
    reader = csv.reader(stream)
    for i, line in enumerate(reader):
        if len(line) != 4:
            return jsonify(message=f'Incorrect number of values on line {str(i)}.'), 400
        try:
            quantity = int(line[2])
        except ValueError:
            return jsonify(message=f'Incorrect quantity on line {str(i)}.'), 400
        if quantity <= 0:
            return jsonify(message=f'Incorrect quantity on line {str(i)}.'), 400
        try:
            price = float(line[3])
        except ValueError:
            return jsonify(message=f'Incorrect price on line {str(i)}.'), 400
        if price <= 0:
            return jsonify(message=f'Incorrect price on line {str(i)}.'), 400

        product_info = {'categories': line[0], 'name': line[1], 'quantity': quantity, 'price': price}
        products.append(product_info)

    products_batch = {'products': products}

    with Redis(host=Configuration.REDIS_HOST) as redis:
        redis.publish(Configuration.REDIS_MESSAGE_CHANNEL, json.dumps(products_batch))

    return Response(status=200)


if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5001)
