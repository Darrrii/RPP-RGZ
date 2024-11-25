from flask import request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Subscription

# Настройка базы данных
DATABASE_URL = "postgresql://username:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def create_subscription():
    data = request.get_json()
    user_id = data.get('user_id')  # Получаем user_id из запроса
    new_subscription = Subscription(
        name=data['name'],
        amount=data['amount'],
        frequency=data['frequency'],  # Исправлено на frequency
        start_date=data['start_date'],
        user_id=user_id  # Устанавливаем user_id
    )
    session.add(new_subscription)
    session.commit()
    return jsonify({'message': 'Subscription created'}), 201

def get_subscriptions():
    subscriptions = session.query(Subscription).all()  # Используем session
    return jsonify([{
        'id': sub.id,
        'name': sub.name,
        'amount': sub.amount,
        'frequency': sub.frequency,  # Исправлено на frequency
        'start_date': sub.start_date
    } for sub in subscriptions])

def update_subscription(subscription_id):
    data = request.get_json()
    subscription = session.query(Subscription).get(subscription_id)  # Используем session
    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404

    subscription.amount = data.get('amount', subscription.amount)
    subscription.frequency = data.get('frequency', subscription.frequency)  # Исправлено на frequency
    subscription.start_date = data.get('start_date', subscription.start_date)
    session.commit()
    return jsonify({'message': 'Subscription updated'})

def delete_subscription(subscription_id):
    subscription = session.query(Subscription).get(subscription_id)  # Используем session
    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404

    session.delete(subscription)
    session.commit()
    return jsonify({'message': 'Subscription deleted'})