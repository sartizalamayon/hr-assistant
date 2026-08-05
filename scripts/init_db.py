"""One-time setup: create the database, enable pgvector, create tables.

Run with: python -m scripts.init_db
"""
import psycopg2
from sqlalchemy import text

from app.config import DATABASE_URL
from app.database import Base, engine

# Import models so they register on Base.metadata before create_all.
from app import models  # noqa: F401


def create_database_if_missing():
    db_name = DATABASE_URL.rsplit("/", 1)[-1]
    admin_url = DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    conn = psycopg2.connect(admin_url)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if cur.fetchone() is None:
            cur.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Created database '{db_name}'.")
        else:
            print(f"Database '{db_name}' already exists.")
    conn.close()


def enable_pgvector():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    print("pgvector extension enabled.")


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created.")


if __name__ == "__main__":
    create_database_if_missing()
    enable_pgvector()
    create_tables()
    print("Database setup complete.")
