import json
import os
import hank
import boto3
from boto3.dynamodb.conditions import Key
from flask import Flask, abort, flash, request, redirect, render_template
from wtforms import Form, TextField, validators

if os.getenv("REDIS_ENABLED"):
    import redis

    redis_host = os.getenv("REDIS_HOST", default="localhost")
    redis_client = redis.Redis(host=redis_host)

app = Flask(__name__)

port = os.getenv("PORT", default=5000)
flask_url = os.getenv("FLASK_URL", default="http://localhost:5000/")
dynamodb_endpoint = os.getenv("DYNAMODB_ENDPOINT", default="http://localhost:8000")

dynamodb = boto3.resource("dynamodb", endpoint_url=dynamodb_endpoint)
table = dynamodb.Table("shortUrl")


class ReusableForm(Form):
    url = TextField("Url:", validators=[validators.required()])


@app.route("/", methods=["GET", "POST"])
def hello():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == "POST":
        url = request.form["url"]
        b58_short = hank.url_to_short_b58(url)

        if form.validate():
            table.put_item(Item={"b58_short": b58_short, "url": url})
            flash(flask_url + b58_short)
        else:
            flash("All the form fields are required. ")

    return render_template("submit.html", form=form)


@app.route("/v1/url", methods=["POST"])
def generate_short_url():
    rtn = {}
    r = request.get_json()
    rtn["url"] = r["url"]
    rtn["b58_short"] = hank.url_to_short_b58(r["url"])
    response = table.put_item(Item={"b58_short": rtn["b58_short"], "url": rtn["url"]})
    return json.dumps(rtn)


@app.route("/<string:b58_short>")
def redirect_from_short(b58_short):
    if not hank.match_b58(b58_short):
        return abort(404)

    if os.getenv("REDIS_ENABLED"):
        try:
            url = redis_client.get(b58_short).decode()
            return redirect(url, code=302)
        except:
            pass

    try:
        response = table.query(KeyConditionExpression=Key("b58_short").eq(b58_short))
        url = response["Items"][0]["url"]
        if os.getenv("REDIS_ENABLED"):
            redis_client.set(b58_short, url)
        return redirect(url, code=302)
    except:
        pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
