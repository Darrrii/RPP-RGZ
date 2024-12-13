import os
import yaml
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/yourdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MigrationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    migration_id = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String, nullable=False)

def apply_migration(file_path):
    with app.app_context():
        with open(file_path, 'r') as f:
            sql = f.read()
            db.session.execute(sql)
            db.session.commit()

def load_changelog():
    with open('changelog.yaml', 'r') as f:
        return yaml.safe_load(f)

def check_migrations():
    changelog = load_changelog()
    applied_migrations = MigrationLog.query.all()
    applied_ids = {m.migration_id for m in applied_migrations}

    for migration in changelog:
        if migration['id'] not in applied_ids:
            try:
                apply_migration(migration['file_path'])
                new_log = MigrationLog(migration_id=migration['id'], file_path=migration['file_path'])
                db.session.add(new_log)
                db.session.commit()
                logging.info(f"Applied migration: {migration['id']}")
            except Exception as e:
                logging.error(f"Error applying migration {migration['id']}: {e}")
                raise RuntimeError("Database is in an inconsistent state.")

@app.before_first_request
def run_migrations():
    db.create_all()
    check_migrations()

if __name__ == '__main__':
    app.run(debug=True)