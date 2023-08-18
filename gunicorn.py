wsgi_app = "config.wsgi:application"
loglevel = "debug"
workers = 2
bind = "localhost:8000"
reload = True
accesslog = errorlog = "/var/log/gunicorn/legitsystems.log"
capture_output = True
pidfile = "/var/run/gunicorn/legitsystems.pid"
daemon = True
