import yaml
import os
from . import db

def run_migrations():
    with open('app/changelog.yaml', 'r') as file:
        changelog = yaml.safe_load(file)

    for change in changelog:
        migration_id = change['id']
        file_path = change['file_path']

        # Check if migration has already been applied
        applied_migration = db.session.execute(
            "SELECT * FROM migrations_log WHERE id = :id", {'id': migration_id}
        ).fetchone()

        if not applied_migration:
            # Apply migration
            with open(file_path, 'r') as sql_file:
                sql = sql_file.read()
                db.session.execute(sql)
                db.session.commit()

            # Log migration
            db.session.execute(
                "INSERT INTO migrations_log (id, file_path) VALUES (:id, :file_path)",
                {'id': migration_id, 'file_path': file_path}
            )
            db.session.commit()