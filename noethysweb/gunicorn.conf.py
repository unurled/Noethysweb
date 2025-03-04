bind = "unix:../gunicorn.sock"
pidfile = "../gunicorn.pid"
wsgi_app = "noethysweb.wsgi"
preload_app = False  # Don't preload to allow SIGHUP to reload code
limit_request_line = 8190

logger_class = "glogging.Logger"
accesslog = "/var/www/vhosts/flambeaux.org/logs/sacadoc.flambeaux.org/gunicorn.log"
access_log_format = '{"timestamp":"%({request_start}c)s","server":"gunicorn","ip":"%({x-real-ip}i)s","vhost":"sacadoc.flambeaux.org","c_host":"%({host}i)s","method":"%(m)s","uri":"%(U)s","qs":"%(q)s","status":"%(s)s","timetakenms":"%(M)s","size":"%(B)s","ua":"%(a)s","ref":"%(f)s","outct":"%({content-type}o)s","user":"%({x-user}o)s","uid":"%({x-uid}i)s","country":"%({x-country-code}i)s"}'
