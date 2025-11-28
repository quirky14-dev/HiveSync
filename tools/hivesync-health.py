#!/usr/bin/env python3
"""
HiveSync Health Script
Run with:
    python3 tools/hivesync-health.py
or:
    python3 tools/hivesync-health.py -json

Outputs:
- Postgres connectivity
- Redis connectivity
- Worker heartbeat summary (optional)
- Queue depth summary
- Status: OK / DEGRADED / FAIL
"""

import argparse
import json
import os
import sys
import time
import psycopg2
import redis
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# Environment variables
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_PORT = int(os.getenv("POSTGRES_PORT", 5432))
PG_DB   = os.getenv("POSTGRES_DB", "hivesync")
PG_USER = os.getenv("POSTGRES_USER", "hivesync")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# For worker heartbeat keys
WORKER_HEARTBEAT_PREFIX = "worker:"


def check_postgres():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASS,
            connect_timeout=3,
        )
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)


def check_redis():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        r.ping()
        return True, None
    except Exception as e:
        return False, str(e)


def get_queue_depths():
    """Depth summary for known queues."""
    queues = ["ai_jobs", "preview_build", "cleanup"]
    depths = {}
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        for q in queues:
            depths[q] = r.llen(q)
        return depths
    except:
        return None


def get_worker_heartbeats():
    """Returns a dict of worker → age in seconds."""
    results = {}
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        for key in r.scan_iter(f"{WORKER_HEARTBEAT_PREFIX}*"):
            worker_id = key.decode()
            ts = float(r.get(key) or 0)
            if ts == 0:
                continue
            age = time.time() - ts
            results[worker_id] = age
        return results
    except:
        return None


def colorize_ok(msg):
    return Fore.GREEN + msg + Style.RESET_ALL


def colorize_warn(msg):
    return Fore.YELLOW + msg + Style.RESET_ALL


def colorize_error(msg):
    return Fore.RED + msg + Style.RESET_ALL


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-json", action="store_true", help="Output JSON instead of colored text")
    args = parser.parse_args()

    pg_ok, pg_err = check_postgres()
    rd_ok, rd_err = check_redis()
    queues = get_queue_depths()
    workers = get_worker_heartbeats()

    # Compute overall health
    status = "ok"
    if not pg_ok or not rd_ok:
        status = "fail"
    else:
        # degraded if workers unresponsive
        if workers:
            for age in workers.values():
                if age > 120:  # 2 minutes old
                    status = "degraded"
                    break

    if args.json:
        output = {
            "postgres": pg_ok,
            "postgres_error": pg_err,
            "redis": rd_ok,
            "redis_error": rd_err,
            "queue_depths": queues,
            "worker_heartbeats": workers,
            "status": status,
        }
        print(json.dumps(output, indent=2))
        return

    # Human-readable colored output
    print("\n=== HiveSync Health Check ===\n")

    # Postgres
    if pg_ok:
        print(colorize_ok("✔ Postgres: OK"))
    else:
        print(colorize_error("✖ Postgres: FAIL"))
        print(colorize_error(f"  Error: {pg_err}"))

    # Redis
    if rd_ok:
        print(colorize_ok("✔ Redis: OK"))
    else:
        print(colorize_error("✖ Redis: FAIL"))
        print(colorize_error(f"  Error: {rd_err}"))

    # Queues
    print("\nQueue Depths:")
    if queues:
        for q, depth in queues.items():
            print(f"  • {q}: {depth}")
    else:
        print("  (Unable to fetch queue depths)")

    # Workers
    print("\nWorkers:")
    if workers:
        for worker_id, age in workers.items():
            age_str = f"{age:.1f}s ago"
            if age > 120:
                print(colorize_warn(f"  • {worker_id}: Unresponsive ({age_str})"))
            else:
                print(colorize_ok(f"  • {worker_id}: Alive ({age_str})"))
    else:
        print("  (No worker heartbeat info)")

    print(f"\nOverall Status: {status.upper()}\n")


if __name__ == "__main__":
    main()
