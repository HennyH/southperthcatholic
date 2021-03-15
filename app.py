import os
import sys
import argparse
from operator import itemgetter
from bottle import route, run, request, template, response, static_file, \
    abort, view, default_app
from hashlib import sha512
from base64 import b64encode

GALLERY_NAMES = ["photos", "saints", "solemnities"]


def hash_password(plain_text, salt):
    salted_plain_text = f"{plain_text}+{salt}"
    salted_bytes = salted_plain_text.encode("utf-8")
    salted_hash = sha512()
    salted_hash.update(salted_bytes)
    salted_hash_digest = salted_hash.digest()
    return b64encode(salted_hash_digest)


@route("/bulletin", method="POST")
def upload_bulletin():
    if "password" not in request.forms or \
        hash_password(request.forms.password,
                      request.app.config["admin_salt"]) != \
            request.app.config["admin_password_hash"]:
        abort(400, "Password mismatch")
    if "bulletin" not in request.files or \
            not (bulletin := request.files.bulletin).filename:
        abort(400, "No file")
    bulletin_directory = request.app.config["bulletin_directory"]
    if not bulletin_directory:
        abort(503, "Upload could not be accepted")
    os.makedirs(bulletin_directory, exist_ok=True)
    bulletin.save(os.path.join(bulletin_directory, bulletin.filename),
                  overwrite=True)


@route("/admin", method="GET")
@view("admin")
def admin_bulletin():
    pass


@route("/", method="GET")
@route("/home", method="GET")
@view("home")
def home_page():
    pass


@route("/mass-times", method="GET")
@view("mass-times")
def mass_times():
    pass


@route("/contact-details", method="GET")
@view("contact-details")
def contact_details():
    pass


@route("/bulletin", method="GET")
def get_bulletin():
    bulletin_directory = request.app.config["bulletin_directory"]
    if not bulletin_directory or not os.path.exists(bulletin_directory):
        abort(404, "No bulletin uploaded")
    bulletins = list(os.scandir(bulletin_directory))
    if not bulletins:
        abort(404, "No bulletin uploaded")
    bulletins_ordered_by_date = \
        sorted(bulletins, key=lambda de: de.stat().st_mtime, reverse=True)
    return static_file(filename=bulletins_ordered_by_date[0].name,
                       root=bulletin_directory,
                       download=True)


@route("/gallery/<gallery_name>", method="GET")
@view("gallery.html")
def gallery(gallery_name):
    if gallery_name not in GALLERY_NAMES:
        abort(404, "No such gallery")
    return {
        "images": [
            [f"/static/images/{gallery_name}/{img.name}", None, None]
            for img in os.scandir(f"static/images/{gallery_name}")
        ]
    }


@route("/static/<resource_type:re:css|docs|images|js>/<path:path>")
def static(resource_type, path):
    is_download = resource_type == "docs"
    return static_file(path, root=f"static/{resource_type}", download=is_download)


@route("/favicon.ico")
def favicon():
    return static_file("images/favicon.ico", root="static")


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--bulletin-directory", type=str, default="bulletins")
    parser.add_argument("--admin-salt", type=str, default="SaltySalt")
    parser.add_argument("--admin-password", type=str, default="test")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--debug", action="store_true")
    result = parser.parse_args(argv)

    app = default_app()
    app.config["port"] = result.port
    app.config["host"] = result.host
    app.config["debug"] = result.debug
    app.config["bulletin_directory"] = result.bulletin_directory
    app.config["admin_salt"] = result.admin_salt
    app.config["admin_password_hash"] = hash_password(result.admin_password,
                                                      salt=result.admin_salt)
    return app


if __name__ == "__main__":
    app = main()
    run(app=app, host=app.config["host"],
        port=app.config["port"], debug=app.config["debug"])
