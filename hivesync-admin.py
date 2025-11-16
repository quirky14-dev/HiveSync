#!/usr/bin/env python3
"""
HiveSync Admin CLI (Docker-aware, Helper Menu, Full Migration Export)

Single-admin automation for:
  - backup (with Docker-aware Postgres dumps)
  - restore (with Docker-aware Postgres restore)
  - migrate (profiles + registry)
  - deploy (docker compose)
  - status (HTTP health + registry)
  - full export for migration (code + DB + configs)

Easy mode:
  python hivesync-admin.py
  python hivesync-admin.py easy

Advanced mode (direct):
  python hivesync-admin.py backup --db --logs --out ./backups
  python hivesync-admin.py restore --from backups/backup_YYYYMMDD_HHMMSS.tar.gz --db
  python hivesync-admin.py migrate --target production
  python hivesync-admin.py deploy --env prod --orchestrator docker
  python hivesync-admin.py status
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.request import urlopen, Request
from urllib.error import URLError

# ---------- Paths & Constants ----------

ROOT = Path(__file__).resolve().parent
DEFAULT_EXPORTS = ROOT / "exports"
DEFAULT_ARCHIVES = ROOT / "archives"
DEFAULT_CONFIG = ROOT / "config"
DEFAULT_LOGS = ROOT / "logs"
DEFAULT_BACKUPS = ROOT / "backups"
DEFAULT_PROFILES = DEFAULT_CONFIG / "migration_profiles.json"
DEFAULT_SUMMARY = DEFAULT_LOGS / "last_admin_summary.txt"

EXPECTED_DIRS = [
    DEFAULT_EXPORTS,
    DEFAULT_ARCHIVES,
    DEFAULT_CONFIG,
    DEFAULT_LOGS,
    DEFAULT_BACKUPS,
    ROOT / "backend",
    ROOT / "shared",
]

# Default Docker container name for Postgres in your docker-compose.yml
DEFAULT_PG_CONTAINER = "hivesync_db"


# ---------- Simple color helper ----------

def c(text: str, color: str) -> str:
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


# ---------- Shell helpers ----------

def sh(cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None, dry: bool = False) -> int:
    """Run a shell command with live output. Returns exit code."""
    printable = " ".join(cmd)
    if dry:
        print(c(f"[dry-run] $ {printable}", "yellow"))
        return 0
    print(c(f"$ {printable}", "cyan"))
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env or os.environ,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    return proc.wait()


def timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def ensure_dirs() -> None:
    for d in EXPECTED_DIRS:
        d.mkdir(parents=True, exist_ok=True)


def load_profiles(path: Path = DEFAULT_PROFILES) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Migration profiles not found at {path}. "
            "Create it from migration_profiles.example.json."
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def tar_directory(src_paths: List[Path], out_tar: Path, dry: bool = False) -> Path:
    out_tar.parent.mkdir(parents=True, exist_ok=True)
    if dry:
        print(c(f"[dry-run] tar {src_paths} -> {out_tar}", "yellow"))
        return out_tar
    with tarfile.open(out_tar, "w:gz") as tar:
        for p in src_paths:
            if p.exists():
                tar.add(str(p), arcname=p.name)
    return out_tar


def untar(archive: Path, dest: Path, dry: bool = False) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if dry:
        print(c(f"[dry-run] untar {archive} -> {dest}", "yellow"))
        return
    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(path=dest)


def http_get(url: str, timeout: int = 8) -> tuple[int, str]:
    try:
        req = Request(url, headers={"User-Agent": "HiveSync-Admin/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), resp.read().decode("utf-8", errors="ignore")
    except URLError as e:
        return 0, str(e)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_summary(lines: List[str]) -> None:
    DEFAULT_LOGS.mkdir(parents=True, exist_ok=True)
    DEFAULT_SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(c(f"[summary] Written to {DEFAULT_SUMMARY}", "magenta"))


# ---------- Docker detection helpers ----------

def has_docker() -> bool:
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


def get_pg_container_name(default: str = DEFAULT_PG_CONTAINER) -> Optional[str]:
    if not has_docker():
        return None
    # Try the default container name first
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True,
        )
        names = [n.strip() for n in result.stdout.splitlines() if n.strip()]
        if default in names:
            return default
        # Fallback: look for any container running postgres image
        result2 = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}} {{.Image}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True,
        )
        for line in result2.stdout.splitlines():
            name, *img = line.split()
            image = " ".join(img)
            if "postgres" in image.lower():
                return name
    except Exception:
        return None
    return None


def docker_pg_dump(out_sql: Path) -> bool:
    """
    Dump Postgres DB from inside the Docker container, if available.
    Returns True if successful, False otherwise.
    """
    if not has_docker():
        print(c("[db] Docker not detected; cannot use docker-based pg_dump.", "yellow"))
        return False

    container = get_pg_container_name()
    if not container:
        print(c("[db] No Postgres container detected. Skipping docker pg_dump.", "yellow"))
        return False

    pg_user = os.getenv("POSTGRES_USER", "postgres")
    pg_db = os.getenv("POSTGRES_DB", "hivesync")

    print(c(f"[db] Using Docker container '{container}' for pg_dump (db={pg_db}, user={pg_user})", "blue"))
    out_sql.parent.mkdir(parents=True, exist_ok=True)

    try:
        with out_sql.open("wb") as f:
            proc = subprocess.run(
                ["docker", "exec", "-i", container, "pg_dump", "-U", pg_user, "-d", pg_db],
                stdout=f,
                stderr=sys.stderr,
                check=False,
            )
        if proc.returncode != 0:
            print(c(f"[db] docker pg_dump returned {proc.returncode}", "red"))
            return False
    except Exception as e:
        print(c(f"[db] docker pg_dump failed: {e}", "red"))
        return False

    print(c(f"[db] Docker pg_dump completed: {out_sql}", "green"))
    return True


def docker_pg_restore(in_sql: Path) -> bool:
    """
    Restore Postgres dump into Docker container, if available.
    Returns True if successful, False otherwise.
    """
    if not has_docker():
        print(c("[db] Docker not detected; cannot use docker-based psql restore.", "yellow"))
        return False

    container = get_pg_container_name()
    if not container:
        print(c("[db] No Postgres container detected. Skipping docker psql restore.", "yellow"))
        return False

    pg_user = os.getenv("POSTGRES_USER", "postgres")
    pg_db = os.getenv("POSTGRES_DB", "hivesync")

    if not in_sql.exists():
        print(c(f"[db] SQL file not found: {in_sql}", "red"))
        return False

    print(c(f"[db] Restoring DB into Docker container '{container}' from {in_sql.name}", "blue"))
    try:
        with in_sql.open("rb") as f:
            proc = subprocess.run(
                ["docker", "exec", "-i", container, "psql", "-U", pg_user, "-d", pg_db],
                stdin=f,
                stderr=sys.stderr,
                check=False,
            )
        if proc.returncode != 0:
            print(c(f"[db] docker psql returned {proc.returncode}", "red"))
            return False
    except Exception as e:
        print(c(f"[db] docker psql failed: {e}", "red"))
        return False

    print(c("[db] Docker psql restore completed.", "green"))
    return True


# ---------- Core Actions ----------

def action_backup(args: argparse.Namespace) -> None:
    ensure_dirs()
    ts = timestamp()
    bundle_name = f"backup_{ts}.tar.gz"
    out_dir = Path(args.out or DEFAULT_BACKUPS)
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / bundle_name

    backup_summary = [f"Backup started at {datetime.utcnow().isoformat()}Z"]

    # Optional DB dump
    db_dump_path = DEFAULT_EXPORTS / "migrations" / f"migration_{ts}.sql"
    if args.db:
        print(c("[backup] Preparing to dump database...", "blue"))
        success = False

        # 1) Try Docker-based dump first
        success = docker_pg_dump(db_dump_path)

        # 2) Fallback: host pg_dump if docker failed
        if not success:
            pg_host = os.getenv("PGHOST", "localhost")
            pg_user = os.getenv("PGUSER", os.getenv("POSTGRES_USER", "postgres"))
            pg_db = os.getenv("PGDATABASE", os.getenv("POSTGRES_DB", "hivesync"))
            print(c(f"[backup] Docker pg_dump unavailable; trying host pg_dump (db={pg_db}, host={pg_host})", "yellow"))
            db_dump_path.parent.mkdir(parents=True, exist_ok=True)
            code = sh(
                ["pg_dump", "-h", pg_host, "-U", pg_user, "-d", pg_db, "-Fc", "-f", str(db_dump_path)],
                dry=args.dry_run,
            )
            success = (code == 0)

        if not success:
            print(c("[backup] WARNING: Database dump failed. Continuing backup of files only.", "red"))
            backup_summary.append("DB dump: FAILED")
        else:
            backup_summary.append(f"DB dump: {db_dump_path}")
    else:
        print(c("[backup] Skipping database dump (use --db to enable).", "yellow"))
        backup_summary.append("DB dump: skipped")

    include_paths = [DEFAULT_EXPORTS, DEFAULT_ARCHIVES, DEFAULT_CONFIG, DEFAULT_LOGS]
    print(c(f"[backup] Including directories: {', '.join(str(p) for p in include_paths)}", "blue"))

    tar_directory(include_paths, bundle_path, dry=args.dry_run)
    print(c(f"[backup] Backup bundle created at: {bundle_path}", "green"))
    backup_summary.append(f"Backup bundle: {bundle_path}")

    write_summary(backup_summary)


def action_restore(args: argparse.Namespace) -> None:
    ensure_dirs()
    src = Path(args.from_path)
    if not src.exists():
        print(c(f"[restore] Backup not found: {src}", "red"), file=sys.stderr)
        sys.exit(1)
    print(c(f"[restore] Restoring from {src}", "blue"))
    untar(src, ROOT, dry=args.dry_run)

    summary = [f"Restore started at {datetime.utcnow().isoformat()}Z", f"Source: {src}"]

    # Optional DB restore
    if args.db and not args.dry_run:
        mig_dir = DEFAULT_EXPORTS / "migrations"
        dumps = sorted(mig_dir.glob("migration_*.sql"), reverse=True)
        if dumps:
            dump = dumps[0]
            print(c(f"[restore] Attempting DB restore from {dump.name}", "blue"))
            success = False

            # 1) Try Docker-based restore
            success = docker_pg_restore(dump)

            # 2) Fallback: host psql
            if not success:
                pg_host = os.getenv("PGHOST", "localhost")
                pg_user = os.getenv("PGUSER", os.getenv("POSTGRES_USER", "postgres"))
                pg_db = os.getenv("PGDATABASE", os.getenv("POSTGRES_DB", "hivesync"))
                print(c("[restore] Docker restore failed/unavailable; trying host psql...", "yellow"))
                if dump.suffix == ".sql":
                    code = sh(
                        ["psql", "-h", pg_host, "-U", pg_user, "-d", pg_db, "-f", str(dump)],
                        dry=args.dry_run,
                    )
                else:
                    code = sh(
                        ["pg_restore", "-h", pg_host, "-U", pg_user, "-d", pg_db, str(dump)],
                        dry=args.dry_run,
                    )
                success = (code == 0)

            if not success:
                print(c("[restore] WARNING: Database restore failed.", "red"))
                summary.append(f"DB restore: FAILED from {dump}")
            else:
                summary.append(f"DB restored from {dump}")
        else:
            print(c("[restore] No migration_*.sql file found for DB restore.", "yellow"))
            summary.append("DB restore: no dump found")
    else:
        summary.append("DB restore: skipped")

    print(c("[restore] Restore complete.", "green"))
    write_summary(summary)


def action_migrate(args: argparse.Namespace) -> None:
    """Non-interactive migrate (used by advanced / scripted flows)."""
    ensure_dirs()
    profiles = load_profiles(Path(args.profiles) if args.profiles else DEFAULT_PROFILES)
    if args.target not in profiles:
        print(c(f"[migrate] Unknown target '{args.target}'. Available: {', '.join(profiles.keys())}", "red"))
        sys.exit(1)
    cfg = profiles[args.target]

    print(c(f"[migrate] Starting migration prep for target: {args.target}", "blue"))

    # 1) Backup current instance
    print(c("[migrate] Step 1: Creating local backup bundle (with DB)...", "blue"))
    backup_args = argparse.Namespace(db=True, logs=True, out=str(DEFAULT_BACKUPS), dry_run=args.dry_run)
    action_backup(backup_args)

    # 2) Export fresh migration script (DB)
    ts = timestamp()
    mig_dir = DEFAULT_EXPORTS / "migrations"
    mig_dir.mkdir(parents=True, exist_ok=True)
    db_dump_path = mig_dir / f"migration_{ts}.sql"
    print(c("[migrate] Step 2: Creating dedicated DB migration script...", "blue"))

    success = docker_pg_dump(db_dump_path)
    if not success:
        pg_host = os.getenv("PGHOST", "localhost")
        pg_user = os.getenv("PGUSER", os.getenv("POSTGRES_USER", "postgres"))
        pg_db = os.getenv("PGDATABASE", os.getenv("POSTGRES_DB", "hivesync"))
        print(c("[migrate] Docker pg_dump unavailable; trying host pg_dump...", "yellow"))
        code = sh(
            ["pg_dump", "-h", pg_host, "-U", pg_user, "-d", pg_db, "-f", str(db_dump_path)],
            dry=args.dry_run,
        )
        if code != 0:
            print(c("[migrate] pg_dump failed; aborting migration prep.", "red"), file=sys.stderr)
            sys.exit(code)

    # 3) Update connection registry
    registry_path = DEFAULT_CONFIG / "connection_registry.json"
    registry = {
        "current_backend_url": cfg.get("current_backend_url", ""),
        "planned_backend_url": cfg.get("planned_backend_url", ""),
        "fallback_backend_url": cfg.get("fallback_backend_url", ""),
        "grace_period": cfg.get("grace_period", ""),
        "note": f"Set by hivesync-admin migrate on {datetime.utcnow().isoformat()}Z",
    }
    write_json(registry_path, registry)
    print(c(f"[migrate] Step 3: Updated {registry_path} with migration URLs.", "green"))

    # 4) Restart orchestrator if requested
    if args.orchestrator == "docker":
        print(c("[migrate] Step 4: Rebuilding & restarting Docker services...", "blue"))
        sh(["docker", "compose", "up", "-d", "--build"], dry=args.dry_run)
    elif args.orchestrator == "pm2":
        print(c("[migrate] Step 4: Restarting PM2 processes...", "blue"))
        sh(["pm2", "restart", "all"], dry=args.dry_run)
    else:
        print(c("[migrate] Step 4: Skipping orchestrator restart (none).", "yellow"))

    summary = [
        f"Migration prep at {datetime.utcnow().isoformat()}Z",
        f"Target profile: {args.target}",
        f"DB migration script: {db_dump_path}",
        f"Connection registry: {registry_path}",
    ]
    write_summary(summary)
    print(c("[migrate] Migration script & config prepared.", "green"))
    print("Use Admin Panel → Push Migration Notice when ready.")


def action_deploy(args: argparse.Namespace) -> None:
    ensure_dirs()
    mode = args.env or os.getenv("HIVESYNC_MODE", "dev")
    print(c(f"[deploy] Deploying in mode={mode}, orchestrator={args.orchestrator}", "blue"))
    if args.orchestrator == "docker":
        sh(["docker", "compose", "up", "-d", "--build"], dry=args.dry_run)
    elif args.orchestrator == "pm2":
        sh(["pm2", "restart", "all"], dry=args.dry_run)
    else:
        print(c("[deploy] No orchestrator specified; skipping service restart.", "yellow"))
    print(c("[deploy] Done.", "green"))


def action_status(args: argparse.Namespace) -> None:
    ensure_dirs()
    api_base = os.getenv("API_BASE_URL", "http://localhost:8080")
    ws_gateway = os.getenv("WS_GATEWAY_URL", "ws://localhost:8080")
    admin_base = os.getenv("ADMIN_BASE_URL", api_base)

    print(c("[status] Checking API /health ...", "blue"))
    code, _ = http_get(f"{api_base}/health")
    print(c(f"[status] API /health -> {code} {'OK' if code == 200 else 'FAIL'}", "green" if code == 200 else "red"))

    print(c("[status] Checking Admin /admin/selfcheck ...", "blue"))
    code2, body2 = http_get(f"{admin_base}/admin/selfcheck")
    print(c(f"[status] Admin /admin/selfcheck -> {code2} {'OK' if code2 == 200 else 'FAIL'}", "green" if code2 == 200 else "red"))

    reg = DEFAULT_CONFIG / "connection_registry.json"
    if reg.exists():
        print(c(f"[status] connection_registry.json:\n{reg.read_text()}", "magenta"))
    else:
        print(c("[status] connection_registry.json not found.", "yellow"))

    print(c(f"[status] WS Gateway configured: {ws_gateway}", "blue"))

    # Docker status (if available)
    if has_docker():
        print(c("[status] Docker detected. Listing containers:", "blue"))
        sh(["docker", "ps"], dry=False)
    else:
        print(c("[status] Docker not detected on this host.", "yellow"))

    print(c("[status] Status check complete.", "green"))


# ---------- Full Migration Export (Replit → Docker or Docker → Docker) ----------

def action_export_full_migration() -> None:
    """
    Full-stack export:
      - DB dump (Docker-aware)
      - exports, archives, config, logs
      - ALL code: backend, shared, desktop, mobile, plugins (if present)
      - docker-compose.yml, Dockerfile, .env
    Produces: migration_bundle_<timestamp>.tar.gz in backups/.
    """
    ensure_dirs()
    print(c("=== HiveSync Full Migration Export ===", "cyan"))
    print("This will:")
    print("  - Create a full backup (DB + configs + logs).")
    print("  - Package ALL code and project files into a single bundle.")
    print("  - Bundle Docker files so you can restore on another Docker host.")
    confirm = input(c("Continue? (Y/n): ", "yellow")).strip().lower()
    if confirm not in ("", "y", "yes"):
        print(c("Aborted by user.", "red"))
        return

    # 1) Run a full backup (includes DB if Docker/pg_dump available)
    print(c("[export] Step 1: Running full backup (DB + logs)...", "blue"))
    backup_args = argparse.Namespace(db=True, logs=True, out=str(DEFAULT_BACKUPS), dry_run=False)
    action_backup(backup_args)

    # 2) Find latest backup tar
    backups = sorted(DEFAULT_BACKUPS.glob("backup_*.tar.gz"), reverse=True)
    if not backups:
        print(c("[export] No backup bundles found after backup step. Aborting.", "red"))
        return
    latest_backup = backups[0]
    print(c(f"[export] Using latest backup bundle: {latest_backup}", "blue"))

    # 3) Define full export contents (code + config + backup + docker files)
    ts = timestamp()
    bundle_name = f"migration_bundle_{ts}.tar.gz"
    bundle_path = DEFAULT_BACKUPS / bundle_name

    include_paths: List[Path] = [
        latest_backup,
        ROOT / "backend",
        ROOT / "shared",
        ROOT / "desktop",
        ROOT / "mobile",
        ROOT / "plugins",
        DEFAULT_CONFIG,
        DEFAULT_EXPORTS,
        DEFAULT_ARCHIVES,
        DEFAULT_LOGS,
        ROOT / "docker-compose.yml",
        ROOT / "Dockerfile",
        ROOT / ".env",
        ROOT / "hivesync-admin.py",
        ROOT / "letsencrypt",
    ]

    include_paths = [p for p in include_paths if p.exists()]

    print(c("[export] Step 2: Creating full migration bundle with:", "blue"))
    for p in include_paths:
        print(f"  - {p}")

    tar_directory(include_paths, bundle_path, dry=False)
    print(c(f"[export] Full migration bundle created at: {bundle_path}", "green"))

    # 4) Compute hash for integrity
    digest = sha256_file(bundle_path)
    print(c(f"[export] SHA-256: {digest}", "magenta"))

    lines = [
        f"Full migration export at {datetime.utcnow().isoformat()}Z",
        f"Backup used: {latest_backup}",
        f"Migration bundle: {bundle_path}",
        f"SHA-256: {digest}",
        "Next steps:",
        "  1) Download the migration bundle from this server.",
        "  2) Upload it to your new server.",
        "  3) On the new server, extract it into /opt/hivesync (or your chosen root).",
        "  4) Run:",
        f"       python3 hivesync-admin.py restore --from {bundle_path.name} --db",
        "  5) Then run:",
        "       docker compose up -d --build",
    ]
    write_summary(lines)

    print()
    print(c("Next steps:", "cyan"))
    print(f"  → Download: {bundle_path}")
    print("  → Upload to your new server.")
    print("  → On the new server:")
    print(f"       python3 hivesync-admin.py restore --from {bundle_path.name} --db")
    print("       docker compose up -d --build")
    print()
    print(c("✅ Full export complete. You now have EVERYTHING needed to move to another host.", "green"))


# ---------- Helper Menu (Easy Mode) ----------

def helper_menu() -> None:
    ensure_dirs()
    while True:
        print()
        print("──────────────────────────────────────────────")
        print(c("      HiveSync Admin Helper Menu", "cyan"))
        print("──────────────────────────────────────────────")
        print("Select an action:")
        print("  1) Backup HiveSync (recommended before any change)")
        print("  2) Restore from a previous backup")
        print("  3) Migrate to a new server (guided)")
        print("  4) Deploy or rebuild services (docker/pm2/none)")
        print("  5) Check system status")
        print("  6) Export EVERYTHING for migration (code + DB + configs)")
        print("  7) Docker → Rebuild & restart (safe deploy)")
        print("  8) Docker → Restart API only")
        print("  9) Docker → Restart all services")
        print(" 10) Exit")
        choice = input(c("Enter a number: ", "yellow")).strip()

        if choice == "1":
            include_db = input("Include database dump? (Y/n): ").strip().lower()
            include_logs = input("Include logs? (Y/n): ").strip().lower()
            args = argparse.Namespace(
                db=(include_db in ("", "y", "yes")),
                logs=(include_logs in ("", "y", "yes")),
                out=str(DEFAULT_BACKUPS),
                dry_run=False,
            )
            action_backup(args)

        elif choice == "2":
            path = input("Path to backup tar.gz: ").strip()
            restore_db = input("Also restore DB from migration_*.sql? (Y/n): ").strip().lower()
            args = argparse.Namespace(
                from_path=path,
                db=(restore_db in ("", "y", "yes")),
                dry_run=False,
            )
            action_restore(args)

        elif choice == "3":
            guided_migrate()

        elif choice == "4":
            env = input("Environment (dev/staging/prod) [prod]: ").strip() or "prod"
            orchestrator = input("Orchestrator (docker/pm2/none) [docker]: ").strip() or "docker"
            args = argparse.Namespace(env=env, orchestrator=orchestrator, dry_run=False)
            action_deploy(args)

        elif choice == "5":
            args = argparse.Namespace()
            action_status(args)

        elif choice == "6":
            action_export_full_migration()

        elif choice == "7":
            if not has_docker():
                print(c("[docker] Docker not detected on this host.", "red"))
            else:
                print(c("[docker] Rebuilding & restarting all services...", "blue"))
                sh(["docker", "compose", "up", "-d", "--build"], dry=False)

        elif choice == "8":
            if not has_docker():
                print(c("[docker] Docker not detected on this host.", "red"))
            else:
                print(c("[docker] Restarting API container only...", "blue"))
                sh(["docker", "compose", "restart", "api"], dry=False)

        elif choice == "9":
            if not has_docker():
                print(c("[docker] Docker not detected on this host.", "red"))
            else:
                print(c("[docker] Restarting all containers...", "blue"))
                sh(["docker", "compose", "restart"], dry=False)

        elif choice == "10":
            print(c("Goodbye.", "green"))
            break

        else:
            print(c("Invalid choice. Please enter a number 1–10.", "red"))


def guided_migrate() -> None:
    """Interactive migration wizard."""
    ensure_dirs()
    print()
    print(c("=== Guided Migration Wizard ===", "cyan"))
    print("This will:")
    print("  - Create a backup and DB dump.")
    print("  - Update migration URLs and grace period (from profiles).")
    print("  - Optionally restart Docker/PM2.")
    print()

    try:
        profiles = load_profiles(DEFAULT_PROFILES)
    except FileNotFoundError as e:
        print(c(str(e), "red"))
        print("Create config/migration_profiles.json first (you can copy migration_profiles.example.json).")
        return

    names = list(profiles.keys())
    if not names:
        print(c("[migrate] No profiles found in migration_profiles.json.", "red"))
        return

    print("Available migration targets:")
    for idx, name in enumerate(names, start=1):
        print(f"  {idx}) {name}")
    sel = input(c("Select a target (number): ", "yellow")).strip()
    try:
        idx = int(sel) - 1
        target = names[idx]
    except (ValueError, IndexError):
        print(c("Invalid selection.", "red"))
        return

    cfg = profiles[target]
    print()
    print(c(f"Selected target: {target}", "cyan"))
    print("Profile details:")
    for k, v in cfg.items():
        print(f"  {k}: {v}")
    cont = input(c("Proceed with this profile? (Y/n): ", "yellow")).strip().lower()
    if cont not in ("", "y", "yes"):
        print(c("Migration cancelled.", "red"))
        return

    orch = input("Orchestrator (docker/pm2/none) [docker]: ").strip() or "docker"
    confirm = input(c("Run migration prep now? (Y/n): ", "yellow")).strip().lower()
    if confirm not in ("", "y", "yes"):
        print(c("Migration cancelled.", "red"))
        return

    args = argparse.Namespace(
        target=target,
        profiles=str(DEFAULT_PROFILES),
        orchestrator=orch,
        dry_run=False,
    )
    action_migrate(args)


# ---------- Argparse (Advanced Mode) ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="HiveSync Admin CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    # backup
    pb = sub.add_parser("backup", help="Create a tar.gz backup bundle")
    pb.add_argument("--db", action="store_true", help="Include PostgreSQL dump")
    pb.add_argument("--logs", action="store_true", help="Include logs directory")
    pb.add_argument("--out", default=str(DEFAULT_BACKUPS), help="Output directory for bundle")
    pb.add_argument("--dry-run", action="store_true", help="Print commands without running")
    pb.set_defaults(func=action_backup)

    # restore
    pr = sub.add_parser("restore", help="Restore from a backup bundle tar.gz")
    pr.add_argument("--from", dest="from_path", required=True, help="Path to backup tar.gz")
    pr.add_argument("--db", action="store_true", help="Restore database if migration_*.sql is present")
    pr.add_argument("--dry-run", action="store_true", help="Print commands without running")
    pr.set_defaults(func=action_restore)

    # migrate
    pm = sub.add_parser("migrate", help="Prepare migration artifacts and update registry")
    pm.add_argument("--target", required=True, help="Target profile name (e.g., production, staging)")
    pm.add_argument("--profiles", help="Path to migration_profiles.json (optional)")
    pm.add_argument("--orchestrator", choices=["docker", "pm2", "none"], default="none", help="Restart services via orchestrator")
    pm.add_argument("--dry-run", action="store_true", help="Print commands without running")
    pm.set_defaults(func=action_migrate)

    # deploy
    pd = sub.add_parser("deploy", help="Rebuild/restart services on current host")
    pd.add_argument("--env", dest="env", help="dev | staging | prod (overrides HIVESYNC_MODE)")
    pd.add_argument("--orchestrator", choices=["docker", "pm2", "none"], default="none")
    pd.add_argument("--dry-run", action="store_true", help="Print commands without running")
    pd.set_defaults(func=action_deploy)

    # status
    ps = sub.add_parser("status", help="Run health checks and print connection registry + Docker status")
    ps.set_defaults(func=action_status)

    return p


# ---------- Main ----------

def main() -> None:
    ensure_dirs()

    # Easy / helper mode:
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "easy"):
        helper_menu()
        return

    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
