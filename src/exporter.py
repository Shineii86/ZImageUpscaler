# ======= • ======= • ======= • ======= • =======• =======
# Z-Image Upscaler — exporter.py
# Repository: https://github.com/Shineii86/ZImageUpscaler
#
# @description
#   Output export utilities. Zips all upscaled images and
#   triggers a browser download in Colab.
#
# @exports
#   zip_outputs, download_zip, cleanup_outputs, get_output_stats
#
# @version 1.0.0
# @author  Shinei Nouzen
# @license MIT
# ======= • ======= • ======= • ======= • =======• =======

import os
import shutil
import subprocess

from . import log

DEFAULT_OUTPUT = "/content/ZImageUpscaler/results"
DEFAULT_ZIP = "/content/ZImage_Upscaled.zip"


def get_output_stats(output_dir=DEFAULT_OUTPUT):
    if not os.path.isdir(output_dir):
        return {"count": 0, "total_mb": 0.0, "files": []}
    files = [f for f in os.listdir(output_dir) if not f.startswith(".")]
    total = sum(os.path.getsize(os.path.join(output_dir, f)) for f in files)
    return {
        "count": len(files),
        "total_mb": total / (1024 ** 2),
        "files": sorted(files),
    }


def cleanup_outputs(output_dir=DEFAULT_OUTPUT, keep_latest=0):
    if not os.path.isdir(output_dir):
        return 0
    files = sorted(
        [os.path.join(output_dir, f) for f in os.listdir(output_dir) if not f.startswith(".")],
        key=os.path.getmtime, reverse=True,
    )
    if not files:
        return 0
    to_remove = files[keep_latest:] if keep_latest > 0 else files
    freed = sum(os.path.getsize(f) for f in to_remove)
    for f in to_remove:
        os.remove(f)
    freed_mb = freed / (1024 ** 2)
    if to_remove:
        log.info(f"🧹 Cleaned {len(to_remove)} files ({freed_mb:.1f} MB freed)")
    return len(to_remove)


def zip_outputs(output_dir=DEFAULT_OUTPUT, zip_path=DEFAULT_ZIP):
    stats = get_output_stats(output_dir)
    if stats["count"] == 0:
        log.warn("No files found in the output directory yet!")
        return None
    log.info(f"🗜️ Zipping {stats['count']} files ({stats['total_mb']:.1f} MB)...")
    all_files = [os.path.join(output_dir, f) for f in stats["files"]]
    subprocess.run(["zip", "-j", "-q", zip_path, *all_files], check=True)
    log.success(f"Zipped to: {zip_path}")
    return zip_path


def download_zip(zip_path=DEFAULT_ZIP):
    try:
        from google.colab import files
        log.info("📥 Initiating download...")
        files.download(zip_path)
    except ImportError:
        log.warn(f"Not running in Colab. Zip saved at: {zip_path}")


__all__ = ["zip_outputs", "download_zip", "cleanup_outputs", "get_output_stats"]
