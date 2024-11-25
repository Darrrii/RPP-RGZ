from flask import request, jsonify
from . import db
from .models import Subscription

def create_subscription():
    data = request.get_json()
    new_subscription = Subscription(
        name=data['name'],
        amount=data['amount'],
        periodicity=data['periodicity'],
        start_date=data['start_date']
    )
    db.session.add(new_subscription)
    db.session.commit()
    return jsonify({'message': 'Subscription created'}), 201

def get_subscriptions():
    subscriptions = Subscription.query.all()
    return jsonify([{
        'id': sub.id,
        'name': sub.name,
        'amount': sub.amount,
        'periodicity': sub.periodicity,
        'start_date': sub.start_date
    } for sub in subscriptions])

def update_subscription(subscription_id):
    data = request.get_json()
    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404

    subscription.amount = data.get('amount', subscription.amount)
    subscription.periodicity = data.get('periodicity', subscription.periodicity)
    subscription.start_date = data.get('start_date', subscription.start_date)
    db.session.commit()
    return jsonify({'message': 'Subscription updated'})

def delete_subscription(subscription_id):
    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404

    db.session.delete(subscription)
    db.session.commit()
    return jsonify({'message': 'Subscription deleted'})