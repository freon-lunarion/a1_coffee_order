# from flask import Flask, request
# from flask_restful import Resource ,Api,reqparse, abort, fields, marshal
# from model import Coffee, Order, Payment
#
# app = Flask(__name__)
# api = Api(app)
# payment_db =[]
#
# coffee_db = [
#     Coffee(1,'short black',2.80),
#     Coffee(2,'long black',3.00),
#     Coffee(3,'cafe latte',3.40),
#     Coffee(4,'cappuccino',3.50),
#     Coffee(5,'flat white',3.60),
# ]
#
# order_counter = 0
# order_db = []
# coffee_field = {
#     'coffee_id':fields.Integer,
#     'coffee_name': fields.String,
#     'cost': fields.Float,
#     'order': fields.Url('orders',absolute=True)
# }
#
#
#
# order_fields = {
#     'order_id': fields.Integer,
#     'coffee_id': fields.Integer,
#     'coffee_name':fields.String,
#     'additions':fields.List(fields.String),
#     'cost': fields.Float,
#     'status': fields.String,
#     'payment': fields.Url('payment_creation',absolute=True),
#
# }
#
# payment_fields = {
#     'order_id': fields.Integer,
#     'payment_type':fields.String,
#     'card_name':fields.String,
#     'card_num':fields.Integer,
#     'card_exp':fields.DateTime
#
# }
#
# class CoffeeList(Resource):
#     def get(self):
#         return marshal([row.__dict__ for row in coffee_db],coffee_field)
#
# class CoffeeInst(Resource):
#     def get(self,coffee_id):
#         row = next((x for x in coffee_db if x.coffee_id == coffee_id), None)
#         return marshal(row.__dict__,coffee_field)
#
# class OrderList(Resource):
#     def get(self):
#         status = request.args.get('status')
#         if status is None:
#             return [row.__dict__ for row in order_db]
#         else:
#             return [row.__dict__ for row in order_db if str(row.status).lower() == str(status).lower()]
#
#     def post(self):
#         global order_counter
#         parser = reqparse.RequestParser()
#         parser.add_argument('coffee_id',type=int,required=True)
#         parser.add_argument('additions', type=str, action='append')
#
#         args = parser.parse_args()
#         coffee_id = args.get("coffee_id")
#         additions = args.get("additions")
#
#         for row in coffee_db:
#             if row.coffee_id == coffee_id:
#                 coffee = row
#                 break
#         else:
#             return abort(404,message="coffee_id {} doesn't exist".format(coffee_id))
#
#         order_counter += 1
#         new = Order(order_counter,coffee_id,coffee.coffee_name,coffee.cost,'open',additions)
#         order_db.append(new)
#
#
#         # return new.__dict__, 201
#         return marshal(new,order_fields) , 201
#
# class OrderInst(Resource):
#     def get(self, order_id):
#         for row in order_db:
#             if int(row.order_id) == int(order_id):
#                 return row.__dict__
#         return abort(404, message="order_id {} doesn't exist".format(order_id))
#
#     def put(self, order_id):
#         # can be updated if status is 'open' and no payment
#         parser = reqparse.RequestParser()
#         parser.add_argument('coffee_id', type=int, required=True)
#         parser.add_argument('additions', type=str, action='append')
#
#         old = next((x for x in order_db if x.order_id == order_id), None)
#         if old is None:
#             return abort(404, message="order_id {} doesn't exist".format(order_id))
#
#         if old.status is not 'open':
#             return abort(401, message="order_id {} cannot be change (not open)".format(order_id))
#
#         is_paid = any(int(row.order_id) == int(order_id) for row in payment_db)
#         if is_paid:
#             return abort(401, message="order_id {} cannot be change (paid)".format(order_id))
#
#         args = parser.parse_args()
#         coffee_id = args.get("coffee_id")
#         additions = args.get("additions")
#         for item in coffee_db:
#             if item.coffee_id == coffee_id:
#                 coffee = item
#                 break
#         else:
#             return abort(404,message="coffee_id {} doesn't exist".format(coffee_id))
#
#         old.coffee_id = coffee_id
#         old.coffee_name = coffee.coffee_name
#         old.cost = coffee.cost
#         old.status = 'open'
#         old.additions = additions
#
#         return marshal(old, order_fields), 201
#
#     def delete(self, order_id):
#         # can be deleted before payment
#
#         row = next((x for x in order_db if x.order_id == order_id),None)
#
#         is_paid = any(int(row.order_id) == int(order_id) for row in payment_db)
#
#         if row is None:
#             return abort(404, message="order_id {} doesn't exist".format(order_id))
#         elif is_paid:
#             return abort(401, message="order_id {} cannot be delete".format(order_id))
#         else:
#             del order_db[order_db.index(row)]
#             return '', 204
#
#     def patch(self, order_id):
#
#         row = next((x for x in order_db if x.order_id == order_id), None)
#         if row is None:
#             return abort(404, message="order_id {} doesn't exist".format(order_id))
#
#         parser = reqparse.RequestParser()
#         args = parser.parse_args()
#         status = args.get("status")
#         is_paid = any(int(row.order_id) == int(id) for row in payment_db)
#         print(status)
#         if is_paid is False and status == 'release':
#             return abort(402, message="order_id {} cannot be release".format(order_id))
#
#         if row.status is not 'open' and status == 'open':
#             return abort(401, message="order_id {}'s status cannot be change".format(order_id))
#
#         row.status = status
#         return row.__dict__, 202
#
# class PaymentOrder(Resource):
#     def post(self,order_id):
#         parser = reqparse.RequestParser()
#         parser.add_argument('payment_type', type=str, required=True)
#         args = parser.parse_args()
#         if not any(row.order_id == order_id for row in order_db):
#             return abort(404, message="order_id {} doesn't exist".format(order_id))
#         payment_type = args.get("payment_type")
#         if payment_type.lower() == 'card':
#             card_name = args.get("card_name")
#             card_num = args.get("card_num")
#             card_exp = args.get("card_exp")
#             new = Payment(order_id, payment_type, card_name, card_num, card_exp)
#         else:
#             new = Payment(order_id, payment_type)
#         payment_db.append(new)
#         return marshal(new.__dict__, payment_fields), 201
#
#     def get(self,order_id):
#         parser = reqparse.RequestParser()
#
#         for row in payment_db:
#             if row.order_id == order_id:
#                 return marshal(row.__dict__, payment_fields)
#         else:
#             return abort(404, message="order_id {} doesn't exist in payment".format(order_id))
#
#
# api.add_resource(CoffeeList, '/coffees',endpoint='coffees')
# api.add_resource(CoffeeInst, '/coffees/<int:coffee_id>', endpoint='coffee')
#
# api.add_resource(OrderList, '/orders',endpoint='orders')
# api.add_resource(OrderInst, '/orders/<int:order_id>', endpoint='order')
#
#
# api.add_resource(PaymentOrder, '/payments/orders/<int:order_id>', endpoint='payment_creation')
# if __name__ == '__main__':
#     app.run(debug=True)