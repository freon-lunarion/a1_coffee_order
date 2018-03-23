from flask import Flask, jsonify, request
from flask_restful import reqparse
from model import Coffee, Order, Payment

app = Flask(__name__)
order_db = []
payment_db = []

order_counter = 0

coffee_db = [
    Coffee(1, 'short black', 2.80),
    Coffee(2, 'long black', 3.00),
    Coffee(3, 'cafe latte', 3.40),
    Coffee(4, 'cappuccino', 3.50),
    Coffee(5, 'flat white', 3.60),
]


@app.route("/orders", methods=['POST'])
def add_order():
    global order_counter
    parser = reqparse.RequestParser()
    parser.add_argument('coffee_type', type=int, required=True)
    parser.add_argument('additions', type=str, action='append')
    args = parser.parse_args()
    order_counter += 1

    coffee_type = args.get("coffee_type")
    additions = args.get("additions")
    for row in coffee_db:
        if int(row.coffee_id) == int(coffee_type):
            cost = row.cost
            break
    else:
        return jsonify(coffee_type=False), 404

    ord = Order(order_counter, coffee_type, cost, 'open', additions)
    order_db.append(ord)

    return jsonify({'data': ord.__dict__, 'link': {'payment': ''}}), 201


@app.route("/orders", methods=['GET'])
def get_orders():
    status = request.args.get('status')

    if status is None:
        return jsonify([st.__dict__ for st in order_db])
    else:
        return jsonify([row.__dict__ for row in order_db if str(row.status).lower() == str(status).lower()])


@app.route('/orders/<int:id>', methods=['GET'])
def get_order_id(id):
    for row in order_db:
        if int(row.order_id) == int(id):
            return jsonify(row.__dict__)
    return jsonify(order_id=False), 404


@app.route("/orders/<id>", methods=['DELETE'])
def delete_order(id):
    # can be deleted before payment
    for row in order_db:

        if int(row.order_id) == int(id):
            order_db.remove(row)
            return jsonify(order_id=id), 204
    return jsonify(order_id=False), 400


@app.route("/orders/<id>", methods=['PUT'])
def update_order(id):
    # can be updated if status is 'open' and no payment
    parser = reqparse.RequestParser()
    parser.add_argument('coffee_type', type=int, required=True)
    parser.add_argument('additions', type=str, action='append')
    args = parser.parse_args()
    coffee_type = args.get("coffee_type")
    additions = args.get("additions")
    for row in coffee_db:
        if int(row.coffee_id) == int(coffee_type):
            cost = row.cost
            break
    else:
        return jsonify(coffee_type=False), 400

    is_paid = any(int(row.order_id) == int(id) for row in payment_db)

    if any(row.order_id == int(id) for row in order_db):
        for row in order_db:
            if int(row.order_id) == int(id) and row.status == 'open' and not is_paid:
                order_db.remove(row)
                new = Order(id, coffee_type, cost, 'open', additions)
                order_db.append(new)
                return jsonify([new.__dict__]), 201
    else:
        return jsonify(order_id=False), 404

    return jsonify(order_id=False), 404


@app.route("/orders/<id>", methods=['PATCH'])
def update_order_status(id):
    parser = reqparse.RequestParser()
    parser.add_argument('coffee_type', type=int)
    args = parser.parse_args()
    status = args.get("status")

    is_paid = any(int(row.order_id) == int(id) for row in payment_db)
    if status == 'release' and is_paid is False:
        return jsonify({'order_id': id, 'status': False}), 403

    for row in order_db:
        if int(row.order_id) == int(id):
            if status == 'release' and is_paid:
                row.status = status
                return jsonify([row.__dict__]), 201
            elif status == 'made':
                row.status = status
                return jsonify([row.__dict__]), 201

    return jsonify(order_id=False), 404


@app.route("/payments", methods=['POST'])
def add_payment():
    parser = reqparse.RequestParser()
    parser.add_argument('order_id', type=int)
    parser.add_argument('payment_type', type=str)
    args = parser.parse_args()

    id = int(args.get("order_id"))

    if not any(row.order_id == id for row in order_db):
        return jsonify(order_id=False), 404

    payment_type = args.get("payment_type")
    if payment_type.lower() == 'card':
        card_name = args.get("card_name")
        card_num = args.get("card_num")
        card_exp = args.get("card_exp")
        payment_db.append((Payment(id, payment_type, card_name, card_num, card_exp)))
    else:
        payment_db.append((Payment(id, payment_type)))

    return jsonify(order_id=id), 201


@app.route("/payments/<id>", methods=['GET'])
def get_payment(id):
    for row in payment_db:
        if int(row.order_id) == int(id):
            return jsonify(row.__dict__)
    return jsonify(order_id=False), 404


if __name__ == "__main__":
    app.run()