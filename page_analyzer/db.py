from datetime import datetime
from psycopg2.extras import NamedTupleCursor


def get_url_by_id(conn, url_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('SELECT * FROM urls WHERE id=%s', (url_id,))
        return cur.fetchone()


def get_check_by_id(conn, url_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('SELECT * FROM url_checks WHERE url_id=%s', (url_id,))
        return cur.fetchall()


def get_url_by_name(conn, url_name):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('SELECT * FROM urls WHERE name=%s', (url_name,))
        return cur.fetchone()


def add_url_by_name(conn, url_name):
    current_date = datetime.now()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('''INSERT INTO urls (name, created_at)
                     VALUES (%s,%s) RETURNING id''',
                    (url_name, current_date,))
        return cur.fetchone()[0]


def get_all_urls(conn):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('SELECT * FROM urls')
        return cur.fetchall()


def get_last_check_url(conn):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('''SELECT DISTINCT ON (url_id) url_id,
                    MAX(created_at) AS created_at,
                    status_code
                    FROM url_checks
                    GROUP BY url_id, status_code
                    ''')
        return cur.fetchall()


def get_analysis_url(conn, url_id, status_code, h1, title, description):
    current_date = datetime.now()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('''INSERT INTO url_checks
                    (url_id, status_code, h1, title,
                    description, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)''',
                    (url_id, status_code, h1, title,
                     description, current_date,)
                    )
