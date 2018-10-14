import base58
import hashlib
import re
import os
import validators as valid
from flask import abort

if os.getenv("REDIS_ENABLED"):
    import redis

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


def url_to_short_b58(url):
    if valid.url(url):
        tmp_hash = hashlib.sha256((url + salt).encode()).hexdigest()
        b58 = base58.b58encode(tmp_hash)
        return b58.decode()[offset : (offset + length)]
    else:
        abort(400)
