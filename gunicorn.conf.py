"""
Gunicorn configuration for AI-Powered Investment Research Platform
Optimized for heavy ML applications with long startup times
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:80"
backlog = 2048

# Worker processes
workers = min(3, multiprocessing.cpu_count())
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout settings - Critical for ML applications
timeout = 300  # 5 minutes for request timeout
keepalive = 5
graceful_timeout = 300  # 5 minutes for graceful shutdown
worker_timeout = 600   # 10 minutes for worker timeout (very important for ML loading)

# Memory and process management
preload_app = False  # Don't preload to avoid memory issues with ML models
reload = False
max_worker_memory = 2000000  # 2GB per worker (adjust based on your EC2 instance)

# Logging
loglevel = "info"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "predictram-research"

# Security
limit_request_line = 8192
limit_request_fields = 200
limit_request_field_size = 8192

# SSL (for production with HTTPS)
# keyfile = "/path/to/ssl/key.pem"
# certfile = "/path/to/ssl/cert.pem"

# Worker lifecycle hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting PredictRAM Research Platform...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading PredictRAM Research Platform...")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"Worker {worker.pid} forked")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker {worker.pid} spawned")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info(f"Worker {worker.pid} initialized")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info(f"Worker {worker.pid} aborted")

# Environment-specific settings
if os.getenv('FLASK_ENV') == 'development':
    reload = True
    loglevel = "debug"
    workers = 1  # Single worker for development

# AWS EC2 optimizations
if os.path.exists('/sys/hypervisor/uuid'):
    # Running on EC2, optimize for cloud environment
    worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance
    tmp_upload_dir = "/tmp"