import os
from operator import itemgetter
from bottle import route, run, request, template, response, static_file, \
    abort, view
from hashlib import sha512
from base64 import b64encode

BULLETIN_DIRECTORY = "bulletins"
ADMIN_SALT = "SaltySalt"
ADMIN_PW_HASH = b"EKrgK7N6azoq50pdu+fc3q2RG4wZXHKkI0QAF7ij7dewyC0VIYZd6g7ctqeiK9eoCULf1tGSsv2b5On/vecUng=="


def hash_password(plain_text):
    salted_plain_text = f"{plain_text}+{ADMIN_SALT}"
    salted_bytes = salted_plain_text.encode("utf-8")
    salted_hash = sha512()
    salted_hash.update(salted_bytes)
    salted_hash_digest = salted_hash.digest()
    return b64encode(salted_hash_digest)


@route("/bulletin", method="POST")
def upload_bulletin():
    if "password" not in request.forms or \
            hash_password(request.forms.password) != ADMIN_PW_HASH:
        abort(400, "Password mismatch")
    if "bulletin" not in request.files or \
            not (bulletin := request.files.bulletin).filename:
        abort(400, "No file")
    os.makedirs(BULLETIN_DIRECTORY, exist_ok=True)
    bulletin.save(os.path.join(BULLETIN_DIRECTORY, bulletin.filename),
                  overwrite=True)


@route("/admin", method="GET")
@view("admin")
def admin_bulletin():
    pass


@route("/bulletin", method="GET")
def get_bulletin():
    if not os.path.exists(BULLETIN_DIRECTORY):
        abort(404, "No bulletin")
    bulletins = list(os.scandir(BULLETIN_DIRECTORY))
    if not bulletins:
        abort(404, "No bulletin")
    bulletins_ordered_by_date = \
        sorted(bulletins, key=lambda de: de.stat().st_mtime, reverse=True)
    return static_file(filename=bulletins_ordered_by_date[0].name,
                       root=BULLETIN_DIRECTORY)


@route("/static/<path:path>")
def static(path):
    return static_file(path, root="static")


@route("/favicon.ico")
def favicon():
    return static_file("images/favicon.ico", root="static")


if __name__ == "__main__":
    run(host="localhost", port=5000)
