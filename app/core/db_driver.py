from typing import Annotated, Any
from fastapi import Depends
import psycopg

# from psycopg2.extras import RealDictCursor # This is meant for v.2
from psycopg.rows import dict_row

DB_CONFIG: dict[str, Any] = {
    "user": "postgres",
    "password": "645798",
    "host": "localhost",
    "port": 5432,
    "dbname": "fastapi",
    "row_factory": dict_row,
}


def get_connection():
    print("Opening connection")
    conn = psycopg.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        print("Closing connection")
        conn.close()


def get_cursor(conn=Depends(get_connection)):  # type: ignore
    cursor: Any = conn.cursor()
    try:
        print("Yielding Cursor")
        yield cursor
        print("After yield: commiting")
        conn.commit()  # Optional: only commit if needed
    finally:
        print("Closing Cursor")
        cursor.close()


Cursor = Annotated[Any, Depends(get_cursor)]
