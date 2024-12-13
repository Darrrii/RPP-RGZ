from flask import Flask, request, render_template, redirect, session
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Функции для работы с базой данных
def db_connect():
    return psycopg2.connect(
        host="127.0.0.1",
        port="5432",
        database="subscriptions_db",
        user="dasharpp_rgz",
        password="123"
    )

def db_close(cursor, connection):
    cursor.close()
    connection.close()

# Главная страница
@app.route("/")
def index():
    return render_template("index.html")

# 1. Создание подписки
@app.route("/subscriptions/new", methods=["GET", "POST"])
def create_subscription():
    if request.method == "GET":
        return render_template("create_subscription.html")
    
    name = request.form.get("name")
    amount = request.form.get("amount")
    frequency = request.form.get("frequency")
    start_date = request.form.get("start_date")

    if not name or not amount or not frequency or not start_date:
        return "Все поля обязательны для заполнения", 400

    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO subscriptions (name, amount, frequency, start_date, user_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, amount, frequency, start_date, session.get("user_id", 1)))  # user_id временно фиксирован

    conn.commit()
    db_close(cur, conn)

    return redirect("/subscriptions")

# 2. Просмотр подписок
@app.route("/subscriptions")
def view_subscriptions():
    conn = db_connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, name, amount, frequency, start_date
        FROM subscriptions
        WHERE user_id = %s
    """, (session.get("user_id", 1),))  # user_id временно фиксирован

    subscriptions = cur.fetchall()
    db_close(cur, conn)

    return render_template("view_subscriptions.html", subscriptions=subscriptions)

# 3. Редактирование подписки
@app.route("/subscriptions/edit/<int:subscription_id>", methods=["GET", "POST"])
def edit_subscription(subscription_id):
    conn = db_connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "GET":
        cur.execute("""
            SELECT id, name, amount, frequency, start_date
            FROM subscriptions
            WHERE id = %s AND user_id = %s
        """, (subscription_id, session.get("user_id", 1)))  # user_id временно фиксирован

        subscription = cur.fetchone()
        db_close(cur, conn)

        if not subscription:
            return "Подписка не найдена", 404

        return render_template("edit_subscription.html", subscription=subscription)

    # Обновление данных подписки
    name = request.form.get("name")
    amount = request.form.get("amount")
    frequency = request.form.get("frequency")
    start_date = request.form.get("start_date")

    cur.execute("""
        UPDATE subscriptions
        SET name = %s, amount = %s, frequency = %s, start_date = %s
        WHERE id = %s AND user_id = %s
    """, (name, amount, frequency, start_date, subscription_id, session.get("user_id", 1)))  # user_id временно фиксирован

    conn.commit()
    db_close(cur, conn)

    return redirect("/subscriptions")

# 4. Удаление подписки
@app.route("/subscriptions/delete/<int:subscription_id>", methods=["POST"])
def delete_subscription(subscription_id):
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM subscriptions
        WHERE id = %s AND user_id = %s
    """, (subscription_id, session.get("user_id", 1)))  # user_id временно фиксирован

    conn.commit()
    db_close(cur, conn)

    return redirect("/subscriptions")

if __name__ == "__main__":
    app.run(debug=True)