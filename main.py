import json
import os
from hank import (
    redis_get,
    redis_set,
    url_to_b58_short,
    write_to_ddb,
    match_b58,
    ddb_get_url,
)
import logging
import boto3
import sys
from boto3.dynamodb.conditions import Key
from flask import Flask, Response, abort, flash, request, redirect, render_template
from wtforms import Form, TextField, validators

if os.getenv("REDIS_ENABLED"):
    import redis

    redis_host = os.getenv("REDIS_HOST", default="localhost")
    redis_client = redis.Redis(host=redis_host)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", default="abc123")

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

port = os.getenv("PORT", default=5000)
flask_url = os.getenv("FLASK_URL", default="http://localhost:5000/")


class ReusableForm(Form):
    url = TextField("Url:", validators=[validators.required()])


@app.route("/", methods=["GET", "POST"])
def hello():
    form = ReusableForm(request.form)

    app.logger.debug(form.errors)
    if request.method == "POST":
        url = request.form["url"]
        b58_short = url_to_b58_short(url)

        if form.validate():
            write_to_ddb(b58_short, url)
            flash(flask_url + "/" + b58_short)
        else:
            flash("All the form fields are required. ")

    return render_template("submit.html", form=form)


@app.route("/url", methods=["POST"])
def generate_short_url():
    r = request.get_json()
    url = r["url"]
    b58_short = url_to_b58_short(url)
    write_to_ddb(b58_short, url)
    rtn = {"b58_short": b58_short, "url": url}
    return Response(json.dumps(rtn), mimetype="application/json")


@app.route("/<string:b58_short>")
def redirect_from_short_url(b58_short):
    if not match_b58(b58_short):
        return abort(404)

    if os.getenv("REDIS_ENABLED"):
        try:
            url = redis_get(b58_short)
            return redirect(url, code=302)
        except:
            pass

    url = ddb_get_url(b58_short)
    if os.getenv("REDIS_ENABLED"):
        redis_set(b58_short, url)

    return redirect(url, code=302)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
