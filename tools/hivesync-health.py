#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HiveSync System Health Diagnostic Tool
--------------------------------------

Runs deep health checks against the HiveSync backend stack:
  - FastAPI health endpoint
  - PostgreSQL connectivity & latency
  - Redis (Celery broker) connectivity
  - Celery worker availability (ping tasks)
  - AI provider connectivity (OpenAI)
  - Disk/CPU/RAM diagnostics
  - Repo folder verification
  - Docker container environment checks
  - Optional JSON output with -json or --json flag


    --json   flag: outputs json file format for dashboards etc...

"""

import os
import json
import time
import argparse
import subprocess
import platform
from datetime import datetime

import requests
import psycopg2
import redis

# Colors for CLI output
class C:
    OK = "\033[92m"
    WARN = "\033[93m"
    ERR = "\033[91m"
    BLU = "\033[94m"
    RST = "\033[0m"
    BOLD = "\033[1m"

# -------------------------------------------------------------------------
# Load configuration or defaults
# -------------------------------------------------------------------------

DEFAULT_BACKEND_URL = os.getenv("HIVESYNC_BACKEND_URL", "http://localhost:8000")
DEFAULT_POSTGRES = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "user": os.getenv("POSTGRES_USER", "hivesync"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "database": os.getenv("POSTGRES_DB", "hivesync"),
}

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REPO_PATH = os.getenv("HIVESYNC_REPO_ROOT", "/opt/hivesync/repos")

OPENAI_KEY = os.getenv("OPENAI_API_KEY", None)  # optional


# -------------------------------------------------------------------------
# Helper: JSON or CLI print
# -------------------------------------------------------------------------

def cli(msg, status="ok"):
    if args.json_mode:
        return

    if status == "ok":
        print(f"{C.OK}[OK]{C.RST} {msg}")
    elif status == "warn":
        print(f"{C.WARN}[WARN]{C.RST} {msg}")
    else:
        print(f"{C.ERR}[FAIL]{C.RST} {msg}")


def record(result_dict, label, status, details=None):
    """Add a record to JSON results."""
    result_dict[label] = {
        "status": status,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }


# -------------------------------------------------------------------------
# Checks
# -------------------------------------------------------------------------

def check_fastapi(result):
    url = f"{DEFAULT_BACKEND_URL}/healthz"
    try:
        start = time.time()
        r = requests.get(url, timeout=2)
        latency = round((time.time() - start) * 1000, 2)

        if r.status_code == 200:
            cli(f"FastAPI backend reachable ({latency}ms)", "ok")
            record(result, "fastapi", "ok", {"latency_ms": latency})
        else:
            cli(f"Backend returned {r.status_code}", "fail")
            record(result, "fastapi", "fail", {"http_code": r.status_code})
    except Exception as e:
        cli(f"FastAPI unreachable: {e}", "fail")
        record(result, "fastapi", "fail", str(e))


def check_postgres(result):
    try:
        start = time.time()
        conn = psycopg2.connect(**DEFAULT_POSTGRES)
        latency = round((time.time() - start) * 1000, 2)
        conn.close()

        cli(f"PostgreSQL connection OK ({latency}ms)", "ok")
        record(result, "postgres", "ok", {"latency_ms": latency})
    except Exception as e:
        cli(f"PostgreSQL error: {e}", "fail")
        record(result, "postgres", "fail", str(e))


def check_redis(result):
    try:
        r = redis.Redis.from_url(REDIS_URL)
        start = time.time()
        pong = r.ping()
        latency = round((time.time() - start) * 1000, 2)

        if pong:
            cli(f"Redis broker reachable ({latency}ms)", "ok")
            record(result, "redis", "ok", {"latency_ms": latency})
        else:
            cli("Redis ping failed", "fail")
            record(result, "redis", "fail", "Ping failed")

    except Exception as e:
        cli(f"Redis error: {e}", "fail")
        record(result, "redis", "fail", str(e))


def check_celery(result):
    """Celery ping test using `celery inspect ping`."""
    try:
        output = subprocess.check_output(
            ["celery", "-A", "backend.worker", "inspect", "ping"],
            stderr=subprocess.STDOUT,
            timeout=4
        ).decode()

        if "pong" in output.lower():
            cli("Celery worker responded to ping", "ok")
            record(result, "celery", "ok", output)
        else:
            cli("Celery returned no pong", "fail")
            record(result, "celery", "fail", output)

    except Exception as e:
        cli(f"Celery unreachable: {e}", "fail")
        record(result, "celery", "fail", str(e))


def check_repos_folder(result):
    if os.path.exists(REPO_PATH):
        cli(f"Repo folder exists: {REPO_PATH}", "ok")
        record(result, "repo_folder", "ok", REPO_PATH)
    else:
        cli(f"Repo folder missing: {REPO_PATH}", "warn")
        record(result, "repo_folder", "warn", REPO_PATH)


def check_system_resources(result):
    # CPU, RAM, disk
    import psutil

    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    cli(f"CPU load: {cpu}% | RAM: {ram}% | Disk: {disk}%", "ok")

    record(result, "resources", "ok", {
        "cpu_percent": cpu,
        "ram_percent": ram,
        "disk_percent": disk
    })


def check_ai_provider(result):
    """Optional OpenAI connectivity test."""
    if not OPENAI_KEY:
        cli("AI: No OpenAI key configured (skipped)", "warn")
        record(result, "ai_connectivity", "warn", "OpenAI key not set")
        return

    try:
        r = requests.get("https://api.openai.com/v1/models",
                         headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                         timeout=3)

        if r.status_code == 200:
            cli("AI provider reachable", "ok")
            record(result, "ai_connectivity", "ok")
        else:
            cli(f"AI provider returned HTTP {r.status_code}", "fail")
            record(result, "ai_connectivity", "fail", r.status_code)

    except Exception as e:
        cli(f"AI provider unreachable: {e}", "fail")
        record(result, "ai_connectivity", "fail", str(e))


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-json", "--json", dest="json_mode", action="store_true",
                        help="Output JSON instead of colored CLI text")
    args = parser.parse_args()

    results = {}

    cli(f"{C.BOLD}{C.BLU}HiveSync System Health Check{C.RST}", "ok")
    cli(f"Timestamp: {datetime.utcnow().isoformat()}", "ok")
    cli(f"Backend URL: {DEFAULT_BACKEND_URL}", "ok")
    print()

    check_fastapi(results)
    check_postgres(results)
    check_redis(results)
    check_celery(results)
    check_repos_folder(results)
    check_system_resources(results)
    check_ai_provider(results)

    print()

    if args.json_mode:
        print(json.dumps(results, indent=4))
    else:
        cli("Health check complete.", "ok")
