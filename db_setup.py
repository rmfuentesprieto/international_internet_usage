import sqlite3


def create_connection(name: str):
    db = sqlite3.connect(name)

    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS international_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT,
        year integer,
        source TEXT,
        usage_percentage REAL,
        UNIQUE(country, year)
    )
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS international_usage_year ON international_usage (year);
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS international_usage_name_year ON international_usage (country, year);
    """)
    db.commit()

    return db
