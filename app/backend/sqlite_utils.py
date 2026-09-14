import sqlite3
from contextlib import contextmanager

DB_PATH = "tutor.db"


@contextmanager
def get_connection():
    con = sqlite3.connect(DB_PATH)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    with get_connection() as con:
        con.execute(
            "CREATE TABLE IF NOT EXISTS query_counts("
            "identifier TEXT, day TEXT, count INTEGER,"
            "PRIMARY KEY (identifier, day))"
        )


def increment_and_get(identifier: str, day: str) -> int:
    with get_connection() as con:
        con.execute(
            "INSERT INTO query_counts (identifier, day, count) VALUES (?, ?, 1) "
            "ON CONFLICT(identifier, day) DO UPDATE SET count = count + 1",
            (identifier, day),
        )
        return con.execute(
            "SELECT count FROM query_counts WHERE identifier = ? AND day = ?",
            (identifier, day),
        ).fetchone()[0]


if __name__ == "__main__":
    init_db()
