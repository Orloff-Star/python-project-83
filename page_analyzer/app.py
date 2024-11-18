from flask import Flask, render_template, request, flash, url_for, redirect
from dotenv import load_dotenv
from urllib.parse import urlparse
import os
import psycopg2
import validators


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

database = os.getenv('DATABASE_URL')


def connection():
    return psycopg2.connect(database)


@app.route('/')
def page_analyzer():
    return render_template('index.html')


@app.get('/urls/<id>')
def url_id(id):
    with connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute('SELECT * FROM urls WHERE id=%s', (id,))
            url_info = cur.fetchone()
    return render_template(
        'url_id.html',
        url=url_info,
    )


@app.post('/urls')
def add_url():
    url_name = request.form.get('url')
    errors = validate(url_name)
    if errors:
        for error in errors.values():
            flash(error, 'error')
        return render_template(
            'index.html',
            url_er=url_name
        ), 422
    parsed_url = urlparse(url_name)
    valid_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    with connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute('SELECT * FROM urls WHERE name=%s', (valid_url,))
            cur_url = cur.fetchone()
            if cur_url:
                flash('Страница уже существует', 'info')
                return redirect(url_for('url_id', id=cur_url.id), code=302)
            cur.execute('INSERT INTO urls (name) VALUES (%s)', (valid_url))
            cur.execute('SELECT * FROM urls WHERE name=%s', (valid_url,))
            cur_url = cur.fetchone()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('url_id', id=cur_url.id))



def validate(url):
    errors = {}
    if len(url) > 255:
        errors['big_len'] = 'URL привышает размер в 255 символов'
    if not validators.url(url):
        errors['invalid'] = 'Некорректный URL'
    if not url:
        errors['empty'] = 'URL не должен быть пустой'
    return errors


if __name__ == '__main__':
 app.run(debug=True)