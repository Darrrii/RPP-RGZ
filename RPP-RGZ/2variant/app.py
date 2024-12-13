from flask import Flask, request, jsonify
from models import db, User, Subscription

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/yourdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/subscriptions', methods=['POST'])
def create_subscription():
    data = request.json
    new_subscription = Subscription(
        name=data['name'],
        amount=data['amount'],
        frequency=data['frequency'],
        user_id=data['user_id']
    )
    db.session.add(new_subscription)
    db.session.commit()
    return jsonify({'message': 'Subscription created'}), 201

@app.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    user_id = request.args.get('user_id')
    subscriptions = Subscription.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': sub.id,
        'name': sub.name,
        'amount': sub.amount,
        'frequency': sub.frequency,
        'start_date': sub.start_date
    } for sub in subscriptions])

@app.route('/subscriptions/<int:id>', methods=['PUT'])
def update_subscription(id):
    data = request.json
    subscription = Subscription.query.get(id)
    if subscription:
        subscription.amount = data.get('amount', subscription.amount)
        subscription.frequency = data.get('frequency', subscription.frequency)
        db.session.commit()
        return jsonify({'message': 'Subscription updated'})
    return jsonify({'message': 'Subscription not found'}), 404

@app.route('/subscriptions/<int:id>', methods=['DELETE'])
def delete_subscription(id):
    subscription = Subscription.query.get(id)
    if subscription:
        db.session.delete(subscription)
        db.session.commit()
        return jsonify({'message': 'Subscription deleted'})
    return jsonify({'message': 'Subscription not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)