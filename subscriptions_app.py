from flask import Flask, request, render_template, redirect, session
import psycopg2
import yaml
from datetime import datetime
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Функция для подключения к базе данных
def db_connect():
    return psycopg2.connect(
        host="127.0.0.1",
        port="5432",
        database="subscriptions_db",
        user="dasharpp_rgz",
        password="123"
    )

def db_close(cur, conn):
    """Закрывает курсор и соединение с базой данных."""
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()

def execute_sql_file(file_path, conn):
    """Выполняет SQL-файл."""
    with open(file_path, "r") as file:
        sql = file.read()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

def run_migrations():
    """Запускает миграции базы данных."""
    conn = db_connect()
    cur = conn.cursor()

    # Создаем таблицу для логирования миграций, если её нет
    cur.execute("""
        CREATE TABLE IF NOT EXISTS migrations_log (
            id SERIAL PRIMARY KEY,
            migration_id INTEGER NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    # Загружаем changelog
    with open("changelog.yaml", "r") as file:
        changelog = yaml.safe_load(file)

    # Получаем список выполненных миграций
    cur.execute("SELECT migration_id, file_path FROM migrations_log")
    applied_migrations = cur.fetchall()
    applied_migrations_dict = {row[0]: row[1] for row in applied_migrations}

    # Проверяем миграции
    for migration in changelog["migrations"]:
        migration_id = migration["id"]
        file_path = migration["file_path"]

        # Если миграция уже выполнена
        if migration_id in applied_migrations_dict:
            if applied_migrations_dict[migration_id] != file_path:
                raise Exception(f"Несоответствие миграции {migration_id}: {file_path} не совпадает с {applied_migrations_dict[migration_id]}")
            continue

        # Выполняем миграцию
        print(f"Применение миграции {migration_id}: {file_path}")
        execute_sql_file(file_path, conn)

        # Логируем миграцию
        cur.execute("""
            INSERT INTO migrations_log (migration_id, file_path)
            VALUES (%s, %s)
        """, (migration_id, file_path))
        conn.commit()

    # Закрываем курсор и соединение
    db_close(cur, conn)

# Запуск мигратора при старте приложения
run_migrations()

# Роуты для работы с подписками
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