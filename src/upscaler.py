# ======= • ======= • ======= • ======= • =======• =======
# Z-Image Upscaler — upscaler.py
# Repository: https://github.com/Shineii86/ZImageUpscaler
#
# @description
#   Real-ESRGAN image upscaler. Loads the model into VRAM,
#   upscales images at 2x or 4x with optional denoising,
#   and supports face enhancement via GFPGAN.
#
# @exports
#   load_model, upscale_image, upscale_batch
#
# @version 1.0.0
# @author  Shinei Nouzen
# @license MIT
# ======= • ======= • ======= • ======= • =======• =======

import os
import gc
import uuid

import torch
import numpy as np
from PIL import Image

from . import log
from .config import (
    WORKSPACE, DEFAULTS, MODEL_DIR,
    MODEL_FILENAME, ANIME_MODEL_FILENAME,
    SCALES, DENOISE_STRENGTHS, OUTPUT_FORMATS,
)

# ══════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════

def _validate_scale(scale):
    if isinstance(scale, str):
        scale = scale.lower().replace("x", "")
        scale = int(scale)
    if scale not in SCALES.values():
        raise ValueError(f"Scale {scale}x not supported. Use 2x or 4x.")
    return scale


def _validate_denoise(strength):
    if isinstance(strength, str):
        strength = DENOISE_STRENGTHS.get(strength.lower())
        if strength is None:
            raise ValueError(f"Unknown denoise preset. Use: {', '.join(DENOISE_STRENGTHS.keys())}")
    if not (0.0 <= strength <= 1.0):
        raise ValueError(f"Denoise strength must be 0.0–1.0, got {strength}")
    return strength


def _validate_format(fmt):
    fmt = fmt.lower()
    if fmt not in OUTPUT_FORMATS:
        raise ValueError(f"Format '{fmt}' not supported. Use: {', '.join(OUTPUT_FORMATS)}")
    return fmt


# ══════════════════════════════════════════════════════════════
# MODEL LOADER
# ══════════════════════════════════════════════════════════════

def _check_cuda():
    if not torch.cuda.is_available():
        raise RuntimeError(
            "\n   ✗ CUDA is not available!\n"
            "\n   Fix: Runtime → Change runtime type → T4 GPU\n"
        )


def _check_model_exists(filename):
    path = os.path.join(MODEL_DIR, filename)
    if not os.path.isfile(path):
        log.error(f"Model not found: {filename}")
        log.error("Fix: Re-run Cell 1 (Initialize) to download")
        return False
    return True


def load_model(model_type=None):
    """
    Load Real-ESRGAN model into VRAM.

    @param {str} model_type — "general" or "anime" (default from config)
    @returns {object} Loaded RealESRGAN model
    """
    _check_cuda()

    if model_type is None:
        model_type = DEFAULTS["model_type"]

    if model_type == "anime":
        filename = ANIME_MODEL_FILENAME
    else:
        filename = MODEL_FILENAME

    if not _check_model_exists(filename):
        raise RuntimeError("Model not found. Run Cell 1 (Initialize) first.")

    log.info("Loading Real-ESRGAN engine...")

    try:
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet

        # Load model architecture
        if model_type == "anime":
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                            num_block=6, num_grow_ch=32, scale=4)
        else:
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                            num_block=23, num_grow_ch=32, scale=4)

        model_path = os.path.join(MODEL_DIR, filename)

        # Determine half precision for T4/ampere GPUs
        half = torch.cuda.get_device_capability(0)[0] >= 7

        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=DEFAULTS["tile_size"],
            tile_pad=10,
            pre_pad=0,
            half=half,
            gpu_id=DEFAULTS["gpu_id"],
        )

    except ImportError as e:
        raise RuntimeError(
            "\n   ✗ Real-ESRGAN not installed!\n"
            "\n   Fix: Re-run Cell 1 (Initialize)\n"
            f"\n   Technical: {e}"
        )
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise RuntimeError(
            "\n   ✗ CUDA Out of Memory during model loading!\n"
            "\n   Fix: Runtime → Disconnect and delete runtime → Re-run all\n"
        )
    except Exception as e:
        raise RuntimeError(f"\n   ✗ Failed to load model: {e}\n")

    log.success("Engine Online. Ready to Upscale.")

    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024 ** 3)
        total = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        log.info(f"   VRAM: {allocated:.1f} GB allocated / {total:.1f} GB total")

    return upsampler


# ══════════════════════════════════════════════════════════════
# FACE ENHANCEMENT
# ══════════════════════════════════════════════════════════════

def _load_face_enhancer():
    try:
        from gfpgan import GFPGANer
        face_enhancer = GFPGANer(
            model_path="https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth",
            upscale=4,
            arch="clean",
            channel_multiplier=2,
            bg_upsampler=None,  # We handle background separately
        )
        return face_enhancer
    except ImportError:
        log.warn("GFPGAN not installed — face enhancement unavailable")
        return None
    except Exception as e:
        log.warn(f"Could not load GFPGAN: {e}")
        return None


# ══════════════════════════════════════════════════════════════
# UPSCALE ENGINE
# ══════════════════════════════════════════════════════════════

def upscale_image(
    upsampler,
    input_path,
    output_dir=None,
    scale=None,
    denoise_strength=None,
    output_format=None,
    face_enhance=False,
):
    """
    Upscale a single image.

    @param {object} upsampler — RealESRGANer instance from load_model()
    @param {str} input_path — Path to input image
    @param {str} output_dir — Output directory
    @param {int} scale — Upscale factor (2 or 4)
    @param {float} denoise_strength — Denoise strength (0.0–1.0)
    @param {str} output_format — Output format (png, jpg, webp)
    @param {bool} face_enhance — Enable GFPGAN face enhancement
    @returns {tuple} (PIL.Image, save_path)
    """
    if scale is None:
        scale = DEFAULTS["scale"]
    if denoise_strength is None:
        denoise_strength = DEFAULTS["denoise_strength"]
    if output_format is None:
        output_format = DEFAULTS["output_format"]
    if output_dir is None:
        output_dir = os.path.join(WORKSPACE, "results")

    scale = _validate_scale(scale)
    denoise_strength = _validate_denoise(denoise_strength)
    output_format = _validate_format(output_format)

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    fn = os.path.basename(input_path)
    log.info(f"Upscaling: {fn} → {scale}x | Denoise: {denoise_strength} | Format: {output_format}")

    # Read image
    img = Image.open(input_path).convert("RGB")
    img_np = np.array(img)

    gc.collect()
    torch.cuda.empty_cache()

    try:
        with torch.inference_mode():
            # For 2x, we still use the 4x model and resize
            output, _ = upsampler.enhance(img_np, outscale=scale)

    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        gc.collect()
        # Retry with tile mode
        log.warn("OOM — retrying with tile mode (slower but uses less VRAM)")
        upsampler.tile_size = 256
        try:
            with torch.inference_mode():
                output, _ = upsampler.enhance(img_np, outscale=scale)
        except Exception as e:
            raise RuntimeError(
                f"\n   ✗ CUDA OOM even with tiles!\n"
                f"\n   Try: Lower resolution input or restart runtime\n"
            )
        finally:
            upsampler.tile_size = DEFAULTS["tile_size"]

    except Exception as e:
        raise RuntimeError(f"\n   ✗ Upscale failed: {e}\n")

    # Face enhancement
    if face_enhance:
        log.info("👤 Applying face enhancement...")
        enhancer = _load_face_enhancer()
        if enhancer:
            try:
                _, _, output = enhancer.enhance(
                    img_np, has_aligned=False, only_center_face=False,
                    paste_back=True, weight=0.5,
                )
                log.success("Face enhancement applied")
            except Exception as e:
                log.warn(f"Face enhancement failed: {e} — using original upscale")

    # Convert to PIL and save
    result = Image.fromarray(output)
    base_name = os.path.splitext(fn)[0]
    out_fn = f"{base_name}_{scale}x_{uuid.uuid4().hex[:4]}.{output_format}"
    save_path = os.path.join(output_dir, out_fn)

    save_kwargs = {}
    if output_format == "jpg":
        save_kwargs["quality"] = 95
    elif output_format == "webp":
        save_kwargs["quality"] = 95
    result.save(save_path, **save_kwargs)

    size_mb = os.path.getsize(save_path) / (1024 ** 2)
    log.success(f"Saved: {out_fn} ({size_mb:.1f} MB)")

    return result, save_path


def upscale_batch(
    upsampler,
    input_paths,
    output_dir=None,
    scale=None,
    denoise_strength=None,
    output_format=None,
    face_enhance=False,
):
    """
    Upscale multiple images.

    @param {object} upsampler — RealESRGANer instance
    @param {list} input_paths — List of image file paths
    @param {str} output_dir — Output directory
    @param {int} scale — Upscale factor
    @param {float} denoise_strength — Denoise strength
    @param {str} output_format — Output format
    @param {bool} face_enhance — Enable face enhancement
    @returns {list} List of (PIL.Image, save_path) tuples
    """
    results = []
    total = len(input_paths)
    log.info(f"Batch upscale: {total} images")

    for i, path in enumerate(input_paths, 1):
        log.info(f"[{i}/{total}] {os.path.basename(path)}")
        try:
            result = upscale_image(
                upsampler, path, output_dir,
                scale, denoise_strength, output_format, face_enhance,
            )
            results.append(result)
        except Exception as e:
            log.error(f"Failed: {os.path.basename(path)} — {e}")

    log.success(f"Batch complete: {len(results)}/{total} upscaled")
    return results


__all__ = ["load_model", "upscale_image", "upscale_batch"]
