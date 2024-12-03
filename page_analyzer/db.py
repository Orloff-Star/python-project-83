import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_url(url_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute('SELECT * FROM urls WHERE id=%s', (url_id,))
            return cur.fetchone()


def get_url_check(url_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute('SELECT * FROM url_checks WHERE url_id=%s', (url_id,))
            return cur.fetchall()


def get_url_by_name(url_name):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute('SELECT * FROM urls WHERE name=%s', (url_name,))
            return cur.fetchone()


def add_url(url_name):
    current_date = datetime.now()
    with get_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute('''INSERT INTO urls (name, created_at)
                        VALUES (%s,%s) RETURNING id''',
                        (url_name, current_date,))
            return cur.fetchone()[0]


def get_urls():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute('SELECT * FROM urls')
            return cur.fetchall()


def get_last_url_check():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute('''SELECT DISTINCT ON (url_id) url_id,
                        MAX(created_at) AS created_at,
                        status_code
                        FROM url_checks
                        GROUP BY url_id, status_code
                        ''')
            return cur.fetchall()


def add_url_check(url_id, status_code, h1, title, description):
    current_date = datetime.now()
    with get_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute('''INSERT INTO url_checks
                        (url_id, status_code, h1, title,
                        description, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)''',
                        (url_id, status_code, h1, title,
                         description, current_date,)
                        )
