# ======= • ======= • ======= • ======= • =======• =======
# Z-Image Upscaler — config.py
# Repository: https://github.com/Shineii86/ZImageUpscaler
#
# @description
#   All configuration constants, model URLs, default parameters,
#   scale presets, and supported option lists.
#
# @exports
#   WORKSPACE, MODEL_URL, MODEL_DIR, MODEL_FILENAME,
#   DEFAULTS, SCALES, DENOISE_STRENGTHS
#
# @version 1.0.0
# @author  Shinei Nouzen
# @license MIT
# ======= • ======= • ======= • ======= • =======• =======

import os

# ══════════════════════════════════════════════════════════════
# PATHS
# ══════════════════════════════════════════════════════════════

WORKSPACE = "/content/ZImageUpscaler"

# Google Drive cache — models persist across Colab restarts
DRIVE_CACHE_DIR = "/content/drive/MyDrive/ZImageUpscaler/models"

# Cache versioning — bump when model URLs change
CACHE_VERSION = "1"

# Disk space thresholds
TOTAL_MODEL_SIZE_GB = 0.1  # Real-ESRGAN is ~65MB
DISK_WARN_GB = 1.0
DISK_MIN_GB  = 0.5

# ══════════════════════════════════════════════════════════════
# MODEL URLS
# ══════════════════════════════════════════════════════════════

# Real-ESRGAN x4plus — best general-purpose upscaler
MODEL_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"

# Real-ESRGAN x4plus anime — optimized for anime/illustration
ANIME_MODEL_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"

MODEL_DIR = os.path.join(WORKSPACE, "weights")
MODEL_FILENAME = "RealESRGAN_x4plus.pth"
ANIME_MODEL_FILENAME = "RealESRGAN_x4plus_anime_6B.pth"

# ══════════════════════════════════════════════════════════════
# DEFAULT PARAMETERS
# ══════════════════════════════════════════════════════════════

DEFAULTS = {
    "scale": 4,              # Upscale factor: 2x or 4x
    "denoise_strength": 0.5, # Denoise strength (0.0–1.0)
    "model_type": "general", # "general" or "anime"
    "output_format": "png",  # Output format: png, jpg, webp
    "face_enhance": False,   # GFPGAN face enhancement
    "tile_size": 0,          # Tile size for low VRAM (0 = auto)
    "gpu_id": 0,             # GPU device ID
}

# ══════════════════════════════════════════════════════════════
# SCALE PRESETS
# ══════════════════════════════════════════════════════════════

SCALES = {
    "2x": 2,   # 2x upscale — good for moderate enhancement
    "4x": 4,   # 4x upscale — maximum quality (default)
}

# Denoise strength presets
DENOISE_STRENGTHS = {
    "none":    0.0,   # No denoising — preserve all detail
    "light":   0.3,   # Light denoising — subtle cleanup
    "medium":  0.5,   # Medium denoising — balanced (default)
    "strong":  0.8,   # Strong denoising — heavy cleanup
    "maximum": 1.0,   # Maximum denoising — aggressive
}

# Supported output formats
OUTPUT_FORMATS = ["png", "jpg", "webp"]

# ══════════════════════════════════════════════════════════════
# EXPORTS
# ══════════════════════════════════════════════════════════════

__all__ = [
    "WORKSPACE", "DRIVE_CACHE_DIR", "CACHE_VERSION",
    "TOTAL_MODEL_SIZE_GB", "DISK_WARN_GB", "DISK_MIN_GB",
    "MODEL_URL", "ANIME_MODEL_URL", "MODEL_DIR",
    "MODEL_FILENAME", "ANIME_MODEL_FILENAME",
    "DEFAULTS", "SCALES", "DENOISE_STRENGTHS", "OUTPUT_FORMATS",
]
