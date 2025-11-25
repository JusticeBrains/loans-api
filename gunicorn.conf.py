import multiprocessing
import os


bind = "unix:/run/gunicorn.sock"

workers_per_core = float(os.getenv("WORKERS_PER_CORE", "1"))
cores = multiprocessing.cpu_count()
default_web_concurrency = workers_per_core * cores + 1
workers = int(os.getenv("WEB_CONCURRENCY", default_web_concurrency))

worker_class = "uvicorn.workers.UvicornWorker"

keepalive = 120
timeout = 120
graceful_timeout = 120

loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"