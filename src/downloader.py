# ======= • ======= • ======= • ======= • =======• =======
# Z-Image Upscaler — downloader.py
# Repository: https://github.com/Shineii86/ZImageUpscaler
#
# @description
#   Model downloader with aria2c acceleration and Google Drive
#   caching. Real-ESRGAN models are ~65MB — fast to download
#   but caching saves time on repeat sessions.
#
# @exports
#   ensure_aria2, mount_drive, download_model, get_cache_status, clear_cache
#
# @version 1.0.0
# @author  Shinei Nouzen
# @license MIT
# ======= • ======= • ======= • ======= • =======• =======

import os
import shutil
import subprocess

from . import log
from .config import (
    DRIVE_CACHE_DIR, CACHE_VERSION, TOTAL_MODEL_SIZE_GB,
    DISK_WARN_GB, DISK_MIN_GB, MODEL_DIR,
)

# ══════════════════════════════════════════════════════════════
# DISK SPACE
# ══════════════════════════════════════════════════════════════

def _free_gb(path="/content"):
    try:
        stat = shutil.disk_usage(path)
        return stat.free / (1024 ** 3)
    except Exception:
        return float("inf")


def check_disk_space(required_gb=TOTAL_MODEL_SIZE_GB):
    free = _free_gb()
    if free < DISK_MIN_GB:
        log.error(f"Only {free:.1f} GB free — need at least {DISK_MIN_GB} GB")
        return False
    if free < DISK_WARN_GB:
        log.warn(f"Only {free:.1f} GB free — things might get tight")
    return True


# ══════════════════════════════════════════════════════════════
# CACHE VERSIONING
# ══════════════════════════════════════════════════════════════

def _version_file():
    return os.path.join(DRIVE_CACHE_DIR, ".cache_version")


def _read_cache_version():
    vf = _version_file()
    if os.path.isfile(vf):
        try:
            return open(vf).read().strip()
        except Exception:
            return None
    return None


def _write_cache_version():
    os.makedirs(DRIVE_CACHE_DIR, exist_ok=True)
    with open(_version_file(), "w") as f:
        f.write(CACHE_VERSION)


def _is_cache_stale():
    stored = _read_cache_version()
    return stored is not None and stored != CACHE_VERSION


# ══════════════════════════════════════════════════════════════
# DRIVE CACHE
# ══════════════════════════════════════════════════════════════

def mount_drive():
    if os.path.isdir("/content/drive/MyDrive"):
        return True
    try:
        from google.colab import drive
        log.info("📂 Mounting Google Drive...")
        drive.mount("/content/drive", force_remount=False)
        return True
    except Exception as e:
        log.warn(f"Could not mount Drive: {e}")
        return False


def _try_load_from_cache(filename, target_dir):
    cache_path = os.path.join(DRIVE_CACHE_DIR, filename)
    dest_path = os.path.join(target_dir, filename)
    if os.path.isfile(cache_path):
        size_mb = os.path.getsize(cache_path) / (1024 ** 2)
        log.info(f"💾 Drive cache hit: {filename} ({size_mb:.0f} MB)")
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(cache_path, dest_path)
        log.success("Copied from Drive cache")
        return True
    return False


def _save_to_cache(filename, source_dir):
    source_path = os.path.join(source_dir, filename)
    cache_path = os.path.join(DRIVE_CACHE_DIR, filename)
    if not os.path.isfile(source_path):
        return
    os.makedirs(DRIVE_CACHE_DIR, exist_ok=True)
    try:
        size_mb = os.path.getsize(source_path) / (1024 ** 2)
        log.info(f"📤 Saving to Drive cache: {filename} ({size_mb:.0f} MB)...")
        shutil.copy2(source_path, cache_path)
        _write_cache_version()
        log.success("Cached to Drive for next session")
    except Exception as e:
        log.warn(f"Could not cache to Drive: {e}")


# ══════════════════════════════════════════════════════════════
# ARIA2C
# ══════════════════════════════════════════════════════════════

def ensure_aria2():
    try:
        subprocess.run(
            ["aria2c", "--version"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        subprocess.run(
            ["apt-get", "-y", "install", "-qq", "aria2"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        log.info("aria2c installed")


# ══════════════════════════════════════════════════════════════
# DOWNLOAD ENGINE
# ══════════════════════════════════════════════════════════════

def download_model(url, filename, target_dir=None, use_drive_cache=True):
    """
    Download a model file. Checks Drive cache first.
    After download, saves to Drive cache for future sessions.

    @param {str} url — Download URL
    @param {str} filename — Target filename
    @param {str} target_dir — Directory to save into
    @param {bool} use_drive_cache — Whether to use Drive cache
    @returns {str} Path to downloaded file
    """
    if target_dir is None:
        target_dir = MODEL_DIR
    os.makedirs(target_dir, exist_ok=True)

    if not check_disk_space():
        raise RuntimeError("Insufficient disk space")

    # Try cache first
    if use_drive_cache:
        if _is_cache_stale():
            log.warn("Cache version mismatch — re-downloading fresh")
        elif _try_load_from_cache(filename, target_dir):
            return os.path.join(target_dir, filename)

    dest = os.path.join(target_dir, filename)
    log.info(f"📥 Downloading: {filename}...")

    cmd = [
        "aria2c", "--console-log-level=error", "--summary-interval=10",
        "-c", "-x", "16", "-s", "16", "-k", "1M",
        "-o", filename, url, "-d", target_dir,
    ]
    subprocess.run(cmd, check=True)

    if os.path.isfile(dest):
        size_mb = os.path.getsize(dest) / (1024 ** 2)
        log.success(f"Downloaded: {filename} ({size_mb:.0f} MB)")
    else:
        raise FileNotFoundError(f"Download succeeded but file not found: {dest}")

    # Save to cache
    if use_drive_cache:
        _save_to_cache(filename, target_dir)

    return dest


def get_cache_status(filenames):
    """Check which models are cached in Drive."""
    status = {"cached": [], "missing": [], "total_mb": 0.0, "stale": False}
    if not os.path.isdir(DRIVE_CACHE_DIR):
        return status
    status["stale"] = _is_cache_stale()
    for fn in filenames:
        cache_path = os.path.join(DRIVE_CACHE_DIR, fn)
        if os.path.isfile(cache_path):
            size = os.path.getsize(cache_path) / (1024 ** 2)
            status["cached"].append({"name": fn, "size_mb": size})
            status["total_mb"] += size
        else:
            status["missing"].append(fn)
    return status


def clear_cache():
    if not os.path.isdir(DRIVE_CACHE_DIR):
        log.info("No cache to clear")
        return
    total = sum(
        os.path.getsize(os.path.join(DRIVE_CACHE_DIR, f))
        for f in os.listdir(DRIVE_CACHE_DIR)
        if os.path.isfile(os.path.join(DRIVE_CACHE_DIR, f))
    )
    shutil.rmtree(DRIVE_CACHE_DIR)
    freed = total / (1024 ** 2)
    log.success(f"Cache cleared — freed {freed:.0f} MB")


__all__ = [
    "ensure_aria2", "mount_drive", "download_model",
    "get_cache_status", "clear_cache", "check_disk_space",
]
