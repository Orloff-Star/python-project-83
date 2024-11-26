from flask import (Flask, render_template, request,
                   flash, url_for, redirect, abort)
from dotenv import load_dotenv
from urllib.parse import urlparse
import os
import validators
import requests
from bs4 import BeautifulSoup
import psycopg2
from page_analyzer import db


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg2.connect(app.config['DATABASE_URL'])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def get_home_page():
    return render_template('index.html')


@app.get('/urls/<url_id>')
def get_page_url(url_id):
    with get_connection() as conn:
        url_info = db.get_url_by_id(conn, url_id)
        url_checks = db.get_check_by_id(conn, url_id)
    if not url_info:
        abort(404)
    return render_template(
        'url_id.html',
        url=url_info,
        url_checks=url_checks,
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
            url_error=url_name
        ), 422
    valid_url = normalize_url(url_name)
    with get_connection() as conn:
        cur_url = db.get_url_by_name(conn, valid_url)
        if cur_url:
            flash('Страница уже существует', 'info')
            return redirect(url_for('get_page_url', url_id=cur_url.id),
                            code=302)
        cur_urls = db.add_url_by_name(conn, valid_url)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_page_url', url_id=cur_urls))


@app.get('/urls')
def get_list_urls():
    with get_connection() as conn:
        urls = db.get_all_urls(conn)
        url_checks = db.get_last_check_url(conn)
    return render_template('urls.html', urls=urls, url_checks=url_checks)


@app.post('/urls/<url_id>/checks')
def url_checks(url_id):
    with get_connection() as conn:
        url_info = db.get_url_by_id(conn, url_id)
        try:
            response = requests.get(url_info.name)
            response.raise_for_status()
        except requests.RequestException:
            flash('Произошла ошибка при проверке', 'error')
            return redirect(url_for('get_page_url', url_id=url_id))
        h1, title, description = get_site_data(response.text)
        db.get_analysis_url(conn, url_id, response.status_code, h1,
                            title, description)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_page_url', url_id=url_id))


def validate(url):
    errors = {}
    if len(url) > 255:
        errors['big_len'] = 'URL привышает размер в 255 символов'
    if not validators.url(url):
        errors['invalid'] = 'Некорректный URL'
    if not url:
        errors['empty'] = 'URL не должен быть пустой'
    return errors


def normalize_url(url):
    parsed_url = urlparse(url)
    valid_url = parsed_url.scheme + '://' + parsed_url.netloc
    return valid_url


def get_site_data(url):
    soup = BeautifulSoup(url, 'html.parser')
    h1 = soup.find('h1').text if soup.find_all('h1') else ''
    title = soup.find('title').text if soup.find_all('title') else ''
    descr_search = soup.find('meta', {'name': 'description'})
    description = descr_search.get('content') if descr_search else ''
    return h1, title, description


if __name__ == '__main__':
    app.run(debug=True)
