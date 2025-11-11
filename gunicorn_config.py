# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:10000"

# Worker processes
workers = 2
worker_class = 'sync'

# Timeout settings (30 minutes)
timeout = 1800
graceful_timeout = 1800

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
