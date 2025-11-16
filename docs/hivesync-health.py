#!/usr/bin/env python3
"""
HiveSync System Health Diagnostics Tool
---------------------------------------

This script performs a detailed health check of your HiveSync backend environment.
It is completely standalone and does NOT interact with or invoke the admin tool.

Features:
- Replit auto-detection (adjusts backend path)
- Detailed CPU metrics (rolling samples)
- Memory usage diagnostics
- Disk usage and backend folder analysis
- SQLite performance tests (read/write latency)
- API latency tests (/health and /admin endpoints)
- Colorized CLI output
- Overall health verdict + migration recommendations

Usage:
    python hivesync-health.py
"""

import os
import sys
import time
import shutil
import math
import sqlite3
import statistics
import threading
from pathlib import Path
from typing import List, Optional

# ------------------------------------------------------------------
# OPTIONAL DEPENDENCIES
# ------------------------------------------------------------------

try:
    import psutil
except ImportError:
    psutil = None

try:
    import requests
except ImportError:
    requests = None


# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------

BACKEND_ROOT = Path(
    os.environ.get("HIVESYNC_BACKEND_ROOT",
                   Path(__file__).resolve().parent)
)

DB_REL_PATH = os.environ.get("HIVESYNC_DB_PATH", "app/hivesync.db")

API_BASE_URL = os.environ.get("HIVESYNC_API_BASE_URL",
                              "http://127.0.0.1:8000")

RUNNING_IN_REPLIT = "REPL_ID" in os.environ

if RUNNING_IN_REPLIT and "HIVESYNC_BACKEND_ROOT" not in os.environ:
    slug = os.environ.get("REPL_SLUG", "").strip()
    if slug:
        inferred = Path(f"/home/runner/{slug}/backend")
        if inferred.exists():
            BACKEND_ROOT = inferred


# ------------------------------------------------------------------
# COLORS & UI
# ------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"

FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_CYAN = "\033[36m"
FG_MAGENTA = "\033[35m"

STATUS_COLORS = {"OK": FG_GREEN, "WARN": FG_YELLOW, "CRIT": FG_RED}


def color(text: str, fg: Optional[str] = None, bold: bool = False) -> str:
    parts = []
    if bold:
        parts.append(BOLD)
    if fg:
        parts.append(fg)
    parts.append(text)
    parts.append(RESET)
    return "".join(parts)


def header(text: str):
    print()
    print(color(f"=== {text} ===", FG_CYAN, bold=True))


def status_label(status: str):
    fg = STATUS_COLORS.get(status, "")
    return color(status, fg, True)


def bar(value: float, max_value: float = 100, width: int = 30):
    ratio = max(0.0, min(1.0, value / max_value))
    filled = int(ratio * width)
    return "[" + "#" * filled + "." * (width - filled) + f"] {value:.1f}%"


def sizeof_fmt(num: float) -> str:
    for unit in ["", "K", "M", "G", "T"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}B"
        num /= 1024.0
    return f"{num:.1f}PB"


def directory_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for child in path.rglob("*"):
        if child.is_file():
            try:
                total += child.stat().st_size
            except OSError:
                pass
    return total


def percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    idx = max(0, min(len(values)-1,
                     int(math.ceil(pct/100 * len(values))) - 1))
    return sorted(values)[idx]





# ------------------------------------------------------------------
# ENVIRONMENT INFO
# ------------------------------------------------------------------

def diag_environment():
    header("Environment Info")
    print("Backend root:", color(str(BACKEND_ROOT), FG_CYAN))
    print("DB path     :", color(str(BACKEND_ROOT / DB_REL_PATH), FG_CYAN))
    print("API base URL:", color(API_BASE_URL, FG_CYAN))
    print("Running in Replit:",
          color(str(RUNNING_IN_REPLIT), FG_MAGENTA))


# ------------------------------------------------------------------
# CPU
# ------------------------------------------------------------------

def diag_cpu():
    header("CPU Diagnostics")

    if psutil is None:
        print(color("psutil not installed — CPU diagnostics unavailable.",
                    FG_RED))
        return "WARN"

    samples = []
    duration = 5
    print("Sampling CPU usage for ~5 seconds...")
    for _ in range(int(duration / 0.5)):
        val = psutil.cpu_percent(interval=0.5)
        samples.append(val)

    current = samples[-1]
    avg = statistics.mean(samples)
    peak = max(samples)

    print("Current:", bar(current))
    print("Avg    :", bar(avg))
    print("Peak   :", bar(peak))

    if peak > 85 or avg > 75:
        return "CRIT"
    elif peak > 65 or avg > 50:
        return "WARN"
    else:
        return "OK"


# ------------------------------------------------------------------
# MEMORY
# ------------------------------------------------------------------

def diag_memory():
    header("Memory Diagnostics")

    if psutil is None:
        print(color("psutil not installed — Memory diagnostics unavailable.",
                    FG_RED))
        return "WARN"

    vm = psutil.virtual_memory()
    used_pct = vm.percent

    print("Total:", sizeof_fmt(vm.total))
    print("Used :", sizeof_fmt(vm.used), f"({used_pct:.1f}%)")
    print("Free :", sizeof_fmt(vm.available))
    print(bar(used_pct))

    if used_pct > 90:
        return "CRIT"
    elif used_pct > 75:
        return "WARN"
    return "OK"


# ------------------------------------------------------------------
# DISK
# ------------------------------------------------------------------

def diag_disk():
    header("Disk / Storage Diagnostics")

    backend_size = directory_size(BACKEND_ROOT)
    db_path = BACKEND_ROOT / DB_REL_PATH
    db_size = db_path.stat().st_size if db_path.exists() else 0

    print("Backend size:", sizeof_fmt(backend_size))
    if db_path.exists():
        print("DB size     :", sizeof_fmt(db_size))
    else:
        print(color("DB file does not exist.", FG_YELLOW))

    status = "OK"

    # thresholds
    if backend_size > 3 * 1024**3:
        status = "CRIT"
    elif backend_size > 1 * 1024**3:
        status = "WARN"

    if db_size > 400 * 1024**2:
        status = "CRIT"
    elif db_size > 250 * 1024**2 and status != "CRIT":
        status = "WARN"

    print("Disk status:", status_label(status))
    return status


# ------------------------------------------------------------------
# SQLITE
# ------------------------------------------------------------------

def diag_sqlite():
    header("SQLite Diagnostics")

    db_path = BACKEND_ROOT / DB_REL_PATH
    if not db_path.exists():
        print(color("DB missing — SQLite tests skipped.", FG_YELLOW))
        return "WARN"

    lat_w = []
    lat_r = []

    try:
        conn = sqlite3.connect(str(db_path), timeout=5)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS __diag_test
                       (id INTEGER PRIMARY KEY AUTOINCREMENT, v TEXT)""")
        conn.commit()

        N = 40
        print(f"Running {N} write/read operations...")
        for i in range(N):
            start = time.perf_counter()
            cur.execute("INSERT INTO __diag_test (v) VALUES (?)", (f"v{i}",))
            conn.commit()
            lat_w.append((time.perf_counter() - start) * 1000)

            start = time.perf_counter()
            cur.execute("SELECT v FROM __diag_test WHERE id = ?",
                        (cur.lastrowid,))
            cur.fetchone()
            lat_r.append((time.perf_counter() - start) * 1000)

        w_p95 = percentile(lat_w, 95)
        r_p95 = percentile(lat_r, 95)

        print(f"Write p95 latency: {w_p95:.2f} ms")
        print(f"Read  p95 latency: {r_p95:.2f} ms")

        if w_p95 > 150 or r_p95 > 150:
            return "CRIT"
        elif w_p95 > 50 or r_p95 > 50:
            return "WARN"
        return "OK"

    except sqlite3.OperationalError as e:
        print(color(f"SQLite error: {e}", FG_RED))
        return "CRIT"

    finally:
        if 'conn' in locals():
            conn.close()
            
# ------------------------------------------------------------------
# API LATENCY
# ------------------------------------------------------------------

def _lat_worker(url, count, results):
    if requests is None:
        return
    for _ in range(count):
        start = time.perf_counter()
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            results.append((time.perf_counter() - start) * 1000)
        except Exception:
            results.append(5000.0)


def diag_api():
    header("API Latency Diagnostics")

    if requests is None:
        print(color("requests not installed — API diagnostics unavailable.",
                    FG_RED))
        return "WARN"

    endpoints = [
        ("Health", f"{API_BASE_URL.rstrip('/')}/health/"),
        ("Admin Users", f"{API_BASE_URL.rstrip('/')}/admin/users"),
    ]

    worst = "OK"

    for name, url in endpoints:
        print()
        print(color(f"-- {name}: {url}", FG_BLUE, True))

        results = []
        threads = []
        for _ in range(5):  # simulate light-medium load
            t = threading.Thread(target=_lat_worker,
                                 args=(url, 4, results),
                                 daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        failures = sum(1 for x in results if x == 5000.0)
        good = [x for x in results if x != 5000.0]

        if not good:
            print(color("Endpoint unreachable.", FG_RED))
            status = "CRIT"
        else:
            p95 = percentile(good, 95)
            avg = statistics.mean(good)
            med = percentile(good, 50)

            print(f"Requests: {len(results)} (failures: {failures})")
            print(f"Median : {med:.2f} ms")
            print(f"Avg    : {avg:.2f} ms")
            print(f"p95    : {p95:.2f} ms")

            if p95 > 600 or failures > 2:
                status = "CRIT"
            elif p95 > 250:
                status = "WARN"
            else:
                status = "OK"

        print("Status:", status_label(status))

        # update global status
        if status == "CRIT":
            worst = "CRIT"
        elif status == "WARN" and worst == "OK":
            worst = "WARN"

    return worst


# ------------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------------

def final_summary(cpu, mem, disk, sqlite_s, api):
    header("Overall HiveSync Health Summary")

    print("CPU   :", status_label(cpu))
    print("Memory:", status_label(mem))
    print("Disk  :", status_label(disk))
    print("SQLite:", status_label(sqlite_s))
    print("API   :", status_label(api))
    print()

    statuses = [cpu, mem, disk, sqlite_s, api]

    if "CRIT" in statuses:
        overall = "CRIT"
    elif "WARN" in statuses:
        overall = "WARN"
    else:
        overall = "OK"

    print(color("OVERALL:", FG_CYAN, True), status_label(overall))
    print()

    if overall == "OK":
        print(color("System appears healthy. 👍", FG_GREEN))
    elif overall == "WARN":
        print(color("Warning signs detected — consider planning migrations:",
                    FG_YELLOW, True))
        print("- Monitor DB file size")
        print("- Watch memory usage")
        print("- Keep an eye on API latency")
        print("- Consider upgrading storage or DB soon")
    else:
        print(color("⚠️  Critical issues detected — action required.", FG_RED, True))
        print("- Migrate SQLite → Postgres")
        print("- Move file storage to S3/Spaces")
        print("- Use separate workers for heavy jobs")
        print("- Consider higher compute or leaving Replit")


# ------------------------------------------------------------------
# MAIN EXECUTION
# ------------------------------------------------------------------

def main():
    diag_environment()
    cpu_s = diag_cpu()
    mem_s = diag_memory()
    disk_s = diag_disk()
    sqlite_s = diag_sqlite()
    api_s = diag_api()
    final_summary(cpu_s, mem_s, disk_s, sqlite_s, api_s)


if __name__ == "__main__":
    main()
