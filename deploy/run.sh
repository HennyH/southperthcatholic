docker build -t southperthcatholic . \
    && docker run -p 8080:5000 southperthcatholic gunicorn --bind 0.0.0.0:5000 "app:main(['--admin-password', '$ADMIN_PASSWORD'])"
