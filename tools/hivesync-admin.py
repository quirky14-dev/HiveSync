#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HiveSync Admin CLI (PostgreSQL + Redis + Docker-aware)

Single-admin utility for:
  - backup (PostgreSQL dumps)
  - restore (from previous dumps)
  - status (calls FastAPI + health script)
  - export (code + DB + configs for migration)
  - simple docker-compose helpers

Usage (menu):
  python hivesync-admin.py

Direct commands:
  python hivesync-admin.py status
  python hivesync-admin.py backup
  python hivesync-admin.py restore
  python hivesync-admin.py export
  python hivesync-admin.py deploy
  python hivesync-admin.py up
  python hivesync-admin.py down
"""

import os
import sys
import json
import time
import tarfile
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# ---------------------------------------------------------------------------
# Configuration (environment-aware)
# ---------------------------------------------------------------------------

HIVESYNC_ROOT = Path(os.getenv("HIVESYNC_ROOT", "/opt/hivesync")).resolve()
BACKUP_DIR = Path(os.getenv("HIVESYNC_BACKUP_DIR", str(HIVESYNC_ROOT / "backups"))).resolve()
CODE_DIR = Path(os.getenv("HIVESYNC_CODE_DIR", str(HIVESYNC_ROOT))).resolve()
CONFIG_DIR = Path(os.getenv("HIVESYNC_CONFIG_DIR", str(HIVESYNC_ROOT / "config"))).resolve()

# Postgres connection details (for pg_dump/pg_restore)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "hivesync")
POSTGRES_DB   = os.getenv("POSTGRES_DB", "hivesync")

# If running inside docker-compose, this should match your service/container name
PG_DOCKER_SERVICE = os.getenv("HIVESYNC_PG_SERVICE", "hivesync_db")

# Path to the health script we previously wrote
HEALTH_SCRIPT = Path(os.getenv("HIVESYNC_HEALTH_SCRIPT", str(HIVESYNC_ROOT / "tools" / "hivesync-health.py")))

DOCKER_COMPOSE_FILE = Path(os.getenv("HIVESYNC_COMPOSE_FILE", str(HIVESYNC_ROOT / "docker-compose.yml")))

# ---------------------------------------------------------------------------
# CLI Color Helper
# ---------------------------------------------------------------------------

class C:
    RED = "\033[31m"
    GRN = "\033[32m"
    YEL = "\033[33m"
    BLU = "\033[34m"
    CYN = "\033[36m"
    MAG = "\033[35m"
    RST = "\033[0m"
    BLD = "\033[1m"


def c(text: str, color: str) -> str:
    return f"{getattr(C, color, '')}{text}{C.RST}"


# ---------------------------------------------------------------------------
# Shell helper
# ---------------------------------------------------------------------------

def sh(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    dry: bool = False
) -> int:
    """Run a shell command with live output. Returns exit code."""
    printable = " ".join(cmd)
    if dry:
        print(c(f"[dry-run] $ {printable}", "YEL"))
        return 0

    print(c(f"$ {printable}", "CYN"))
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env or os.environ.copy(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in proc.stdout:
        print(line.rstrip())
    proc.wait()
    return proc.returncode


# ---------------------------------------------------------------------------
# Admin actions
# ---------------------------------------------------------------------------

def ensure_dirs():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    (HIVESYNC_ROOT / "tools").mkdir(parents=True, exist_ok=True)


def action_status():
    """Run health checks + quick docker status."""
    print(c("\n=== HiveSync Status ===", "BLD"))

    # 1. Health script (if exists)
    if HEALTH_SCRIPT.exists():
        print(c("\n[1] Internal health script:", "BLU"))
        rv = sh([sys.executable, str(HEALTH_SCRIPT)], dry=False)
        if rv != 0:
            print(c("Health script returned non-zero exit code.", "YEL"))
    else:
        print(c("Health script not found; skipping.", "YEL"))

    # 2. Docker ps (if docker-compose exists)
    if DOCKER_COMPOSE_FILE.exists():
        print(c("\n[2] Docker compose services:", "BLU"))
        sh(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "ps"], dry=False)
    else:
        print(c("\n[2] docker-compose.yml not found; skipping compose status.", "YEL"))

    print()


def _pg_dump_path():
    return shutil.which("pg_dump") or "pg_dump"


def _pg_restore_path():
    return shutil.which("pg_restore") or "pg_restore"


def action_backup(dry: bool = False):
    """Create a timestamped PostgreSQL dump in BACKUP_DIR."""
    ensure_dirs()
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    backup_file = BACKUP_DIR / f"hivesync-db-{ts}.dump"

    print(c("\n=== HiveSync Database Backup ===", "BLD"))
    print(c(f"Backup directory: {BACKUP_DIR}", "BLU"))
    print(c(f"Target: {backup_file}", "BLU"))

    cmd = [
        _pg_dump_path(),
        "-h", POSTGRES_HOST,
        "-p", POSTGRES_PORT,
        "-U", POSTGRES_USER,
        "-F", "c",  # custom format
        "-d", POSTGRES_DB,
        "-f", str(backup_file),
    ]

    # We may need PGPASSWORD environment
    env = os.environ.copy()
    if "POSTGRES_PASSWORD" in env:
        env["PGPASSWORD"] = env.get("POSTGRES_PASSWORD")

    rc = sh(cmd, env=env, dry=dry)
    if rc == 0 and not dry:
        print(c(f"\nBackup complete: {backup_file}", "GRN"))
    elif dry:
        print(c("Dry run complete (backup not actually created).", "YEL"))
    else:
        print(c("Backup failed.", "RED"))


def action_restore(backup_file: Optional[str] = None, dry: bool = False):
    """Restore PostgreSQL from a chosen dump."""
    ensure_dirs()
    print(c("\n=== HiveSync Database Restore ===", "BLD"))

    if backup_file:
        dump = Path(backup_file).expanduser().resolve()
    else:
        dumps = sorted(BACKUP_DIR.glob("hivesync-db-*.dump"))
        if not dumps:
            print(c("No backup files found in backup directory.", "RED"))
            return
        print(c("Available backups:", "BLU"))
        for i, d in enumerate(dumps, start=1):
            print(f"  {i}. {d.name}")
        choice = input(c("Select a backup to restore (number): ", "YEL"))
        try:
            idx = int(choice) - 1
            dump = dumps[idx]
        except Exception:
            print(c("Invalid selection.", "RED"))
            return

    if not dump.exists():
        print(c(f"Backup file not found: {dump}", "RED"))
        return

    print(c(f"Selected backup: {dump}", "BLU"))
    confirm = input(c("THIS WILL OVERWRITE THE DATABASE. Continue? (yes/no): ", "YEL"))
    if confirm.lower() != "yes":
        print(c("Restore cancelled.", "YEL"))
        return

    # Drop & recreate DB or use --clean
    cmd = [
        _pg_restore_path(),
        "-h", POSTGRES_HOST,
        "-p", POSTGRES_PORT,
        "-U", POSTGRES_USER,
        "-d", POSTGRES_DB,
        "--clean",
        str(dump),
    ]

    env = os.environ.copy()
    if "POSTGRES_PASSWORD" in env:
        env["PGPASSWORD"] = env.get("POSTGRES_PASSWORD")

    rc = sh(cmd, env=env, dry=dry)
    if rc == 0 and not dry:
        print(c("\nRestore complete.", "GRN"))
    elif dry:
        print(c("Dry run complete (restore not actually performed).", "YEL"))
    else:
        print(c("Restore failed.", "RED"))


def action_export(dry: bool = False):
    """Create a full export tar.gz (code + config + latest DB dump)."""
    ensure_dirs()
    print(c("\n=== HiveSync Full Export (Code + DB + Config) ===", "BLD"))

    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    export_dir = BACKUP_DIR / f"export-{ts}"
    export_dir.mkdir(parents=True, exist_ok=True)

    # 1) Database dump
    db_dump = export_dir / f"hivesync-db-{ts}.dump"
    print(c("[1] Creating database dump for export...", "BLU"))
    cmd = [
        _pg_dump_path(),
        "-h", POSTGRES_HOST,
        "-p", POSTGRES_PORT,
        "-U", POSTGRES_USER,
        "-F", "c",
        "-d", POSTGRES_DB,
        "-f", str(db_dump),
    ]
    env = os.environ.copy()
    if "POSTGRES_PASSWORD" in env:
        env["PGPASSWORD"] = env.get("POSTGRES_PASSWORD")

    rc = sh(cmd, env=env, dry=dry)
    if rc != 0 and not dry:
        print(c("Database dump failed; export aborted.", "RED"))
        return

    # 2) Copy config
    export_config = export_dir / "config"
    if CONFIG_DIR.exists():
        print(c("[2] Copying config directory...", "BLU"))
        if not dry:
            shutil.copytree(CONFIG_DIR, export_config, dirs_exist_ok=True)
    else:
        print(c("[2] Config directory not found; skipping.", "YEL"))

    # 3) Tar code (excluding backups)
    code_src = CODE_DIR
    tar_path = BACKUP_DIR / f"hivesync-export-{ts}.tar.gz"
    print(c("[3] Creating export tarball...", "BLU"))

    if dry:
        print(c(f"[dry-run] Would create: {tar_path}", "YEL"))
    else:
        with tarfile.open(tar_path, "w:gz") as tar:
            # Code base
            tar.add(str(code_src), arcname="hivesync", filter=lambda info: None if "backups" in info.name else info)
            # DB dump + config
            tar.add(str(export_dir), arcname="export-meta")

        print(c(f"\nExport archive created: {tar_path}", "GRN"))

    # 4) Cleanup temp export_dir (but leave tar + backup dir)
    if not dry:
        shutil.rmtree(export_dir, ignore_errors=True)


def action_docker_up(dry: bool = False):
    """docker-compose up -d for the HiveSync stack."""
    if not DOCKER_COMPOSE_FILE.exists():
        print(c("docker-compose.yml not found; cannot run docker up.", "RED"))
        return
    sh(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "up", "-d"], cwd=HIVESYNC_ROOT, dry=dry)


def action_docker_down(dry: bool = False):
    """docker-compose down for the HiveSync stack."""
    if not DOCKER_COMPOSE_FILE.exists():
        print(c("docker-compose.yml not found; cannot run docker down.", "RED"))
        return
    sh(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "down"], cwd=HIVESYNC_ROOT, dry=dry)


def action_deploy(dry: bool = False):
    """Simple 'deploy' command: docker-compose pull + up."""
    if not DOCKER_COMPOSE_FILE.exists():
        print(c("docker-compose.yml not found; cannot deploy.", "RED"))
        return

    print(c("\n=== HiveSync Deploy (docker-compose) ===", "BLD"))
    sh(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "pull"], cwd=HIVESYNC_ROOT, dry=dry)
    sh(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "up", "-d"], cwd=HIVESYNC_ROOT, dry=dry)

# ---------------------------------------------------------------------------
# New Admin Actions (Cleanup Worker, Notifications, Preview Jobs, Token Decoder)
# ---------------------------------------------------------------------------

def action_cleanup_now():
    """Trigger cleanup worker immediately by pushing a job to the cleanup queue."""
    import redis
    try:
        r = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0)
        r.lpush("cleanup", "manual_trigger")
        print(c("✔ Cleanup job enqueued.", "GRN"))
    except Exception as e:
        print(c(f"✖ Failed to enqueue cleanup job: {e}", "RED"))


def action_clear_notifications():
    """Delete all notifications from the database."""
    import psycopg2
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=int(POSTGRES_PORT),
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM notifications;")
        conn.commit()
        conn.close()
        print(c("✔ All notifications cleared.", "GRN"))
    except Exception as e:
        print(c(f"✖ Failed to clear notifications: {e}", "RED"))


def action_preview_jobs():
    """Show the length of the preview_build queue (simple visibility)."""
    import redis
    r = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0)
    depth = r.llen("preview_build")
    print(c("\n=== Preview Build Queue ===", "BLD"))
    print(c(f"Queue depth: {depth}", "BLU"))


def action_decode_token_payload(payload_b64: str):
    """Decode ONLY the Base64 JSON payload of a stateless token (admin-safe)."""
    import base64
    import json
    try:
        # Add padding for safe decoding
        padded = payload_b64 + "=="
        data = base64.urlsafe_b64decode(padded)
        obj = json.loads(data.decode("utf-8"))
        print(json.dumps(obj, indent=2))
    except Exception as e:
        print(c(f"Failed to decode payload: {e}", "RED"))


# ---------------------------------------------------------------------------
# Menu / argument handling
# ---------------------------------------------------------------------------

def print_menu():
    print()
    print(c("HiveSync Admin Menu", "BLD"))
    print(c("===================", "BLD"))
    print("1) Status (health + docker)")
    print("2) Backup database")
    print("3) Restore database")
    print("4) Full export (code + DB + config)")
    print("5) Docker up")
    print("6) Docker down")
    print("7) Deploy (pull + up)")
    print("8) Cleanup now")
    print("9) Clear all notifications")
    print("10) Preview jobs")
    print("11) Decode token payload (admin-safe)")

    print("0) Exit")
    print()


def interactive_menu():
    while True:
        print_menu()
        choice = input(c("Select an option: ", "YEL")).strip()

        if choice == "1":
            action_status()
        elif choice == "2":
            action_backup()
        elif choice == "3":
            action_restore()
        elif choice == "4":
            action_export()
        elif choice == "5":
            action_docker_up()
        elif choice == "6":
            action_docker_down()
        elif choice == "7":
            action_deploy()
        elif choice == "8":
            action_cleanup_now()
        elif choice == "9":
            action_clear_notifications()
        elif choice == "10":
            action_preview_jobs()
        elif choice == "11":
            payload = input(c("Enter BASE64 payload: ", "YEL")).strip()
            action_decode_token_payload(payload)

        elif choice == "0":
            print(c("Goodbye.", "GRN"))
            break
        else:
            print(c("Invalid selection.", "RED"))


def main(argv: List[str]):
    if len(argv) <= 1:
        interactive_menu()
        return

    cmd = argv[1].lower()
    args = argv[2:]

    dry = "--dry-run" in args or "-n" in args

    if cmd == "status":
        action_status()
    elif cmd == "backup":
        action_backup(dry=dry)
    elif cmd == "restore":
        backup_file = args[0] if args and not args[0].startswith("-") else None
        action_restore(backup_file=backup_file, dry=dry)
    elif cmd == "export":
        action_export(dry=dry)
    elif cmd == "deploy":
        action_deploy(dry=dry)
    elif cmd == "up":
        action_docker_up(dry=dry)
    elif cmd == "down":
        action_docker_down(dry=dry)
    elif cmd == "cleanup-now":
        action_cleanup_now()
    elif cmd == "clear-notifications":
        action_clear_notifications()
    elif cmd == "preview-jobs":
        action_preview_jobs()
    elif cmd == "decode-payload":
        if args:
            action_decode_token_payload(args[0])
        else:
            print("Usage: hivesync-admin.py decode-payload <base64-payload>")

    else:
        print(c(f"Unknown command: {cmd}", "RED"))
        print("Usage:")
        print("  hivesync-admin.py           # interactive menu")
        print("  hivesync-admin.py status")
        print("  hivesync-admin.py backup [--dry-run]")
        print("  hivesync-admin.py restore [path/to/dump] [--dry-run]")
        print("  hivesync-admin.py export [--dry-run]")
        print("  hivesync-admin.py deploy [--dry-run]")
        print("  hivesync-admin.py up [--dry-run]")
        print("  hivesync-admin.py down [--dry-run]")


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print()
        print(c("Interrupted by user.", "YEL"))
