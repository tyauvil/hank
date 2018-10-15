import base58
import hashlib
import re
import os
import validators as valid
from flask import abort
import boto3
from boto3.dynamodb.conditions import Key

if os.getenv("REDIS_ENABLED"):
    import redis

    redis_host = os.getenv("REDIS_HOST", default="localhost")
    redis_client = redis.Redis(host=redis_host)

dynamodb_endpoint = os.getenv("DYNAMODB_ENDPOINT", default="http://localhost:8000")
dynamodb_table = os.getenv("DYNAMODB_TABLE", default="shortUrl")
dynamodb = boto3.resource("dynamodb", endpoint_url=dynamodb_endpoint)
table = dynamodb.Table(dynamodb_table)

salt = os.getenv("SALT", default="ChjXSs55KOFCAb8L")
offset = os.getenv("CODED_OFFSET", default=44)
length = os.getenv("CODED_LENGTH", default=6)

pattern = "[A-Za-z0-9]{{{0}}}".format(length)
regex = re.compile(pattern)


def match_b58(s):
    if len(s) == length:
        return regex.match(s) is not None
    else:
        return False


def url_to_b58_short(url):
    if valid.url(url):
        tmp_hash = hashlib.sha256((url + salt).encode()).hexdigest()
        b58 = base58.b58encode(tmp_hash)
        b58_short = b58.decode()[offset : (offset + length)]
        print(b58_short)
        return b58_short
    else:
        abort(400)


def write_to_ddb(b58_short, url):
    r = table.put_item(Item={"b58_short": b58_short, "url": url})
    print(r)


def ddb_get_url(b58_short):
    r = table.query(KeyConditionExpression=Key("b58_short").eq(b58_short))
    print(r)
    url = r["Items"][0]["url"]
    if os.getenv("REDIS_ENABLED"):
        redis_set(b58_short, url)
    return url


def redis_get(b58_short):
    url = redis_client.get(b58_short).decode()
    return url


def redis_set(b58_short, url):
    redis_client.set(b58_short, url)
