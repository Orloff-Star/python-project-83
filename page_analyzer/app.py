import logging
import os

import requests
from dotenv import load_dotenv
from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)

from page_analyzer import db, functions

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    logging.exception(str(e))
    return render_template("500.html"), 500


@app.route("/")
def get_home_page():
    return render_template("index.html")


@app.get("/urls/<url_id>")
def get_page_url(url_id):
    url_info = db.get_url(url_id)
    url_checks = db.get_url_check(url_id)
    if not url_info:
        abort(404)
    return render_template(
        "url.html",
        url=url_info,
        url_checks=url_checks,
    )


@app.post("/urls")
def post_url():
    url_name = request.form.get("url")
    errors = functions.validate(url_name)
    if errors:
        for error in errors.values():
            flash(error, "error")
        return render_template("index.html", url_error=url_name), 422
    valid_url = functions.normalize_url(url_name)
    url = db.get_url_by_name(valid_url)
    if url:
        flash("Страница уже существует", "info")
        return redirect(url_for("get_page_url", url_id=url.id), code=302)
    url = db.add_url(valid_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("get_page_url", url_id=url))


@app.get("/urls")
def get_list_urls():
    urls = db.get_urls()
    url_checks = {item.url_id: item for item in db.get_last_url_check()}
    return render_template("urls.html", urls=urls, url_checks=url_checks)


@app.post("/urls/<url_id>/checks")
def url_checks(url_id):
    url_info = db.get_url(url_id)
    try:
        response = requests.get(url_info.name)
        response.raise_for_status()
    except requests.RequestException:
        flash("Произошла ошибка при проверке", "error")
        return redirect(url_for("get_page_url", url_id=url_id))
    h1, title, description = functions.get_site_data(response.text)
    db.add_url_check(url_id, response.status_code, h1, title, description)
    flash("Страница успешно проверена", "success")
    return redirect(url_for("get_page_url", url_id=url_id))


if __name__ == "__main__":
    app.run(debug=True)
