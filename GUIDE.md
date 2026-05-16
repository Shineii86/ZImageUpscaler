# 📖 Z-Image Upscaler — User Guide

> **Everything you need to know to upscale images with AI.**
> Written for beginners — no coding experience required.

---

## 🤔 What Is This?

**Z-Image Upscaler** enhances low-resolution images using AI (Real-ESRGAN). It makes images bigger and sharper without losing quality.

```
Upload a blurry/small image → AI enhances it → Download the crisp, high-res result
```

**What makes it special:**
- **4x upscale** — Make images 4× larger with AI detail
- **Free GPU** — Runs on Google Colab's free T4 GPU
- **Face enhance** — Optional GFPGAN for portraits
- **Anime support** — Dedicated model for illustrations

---

## 💻 What You Need

- A Google account (for Colab)
- A web browser
- Images to upscale (JPG, PNG, WEBP)

---

## 🚀 Getting Started

1. Open [ZImageUpscaler.ipynb](https://colab.research.google.com/github/Shineii86/ZImageUpscaler/blob/main/notebook/ZImageUpscaler.ipynb) in Google Colab
2. Set runtime to **T4 GPU**: Runtime → Change runtime type → T4
3. Run cells in order (1 → 2 → 3)

---

## 🔧 Step 1 — Initialize

This cell:
- Installs Real-ESRGAN and dependencies
- Downloads the AI model (~65 MB)
- Sets up the environment

**First run**: ~1–2 minutes for download. **Subsequent runs**: ~10 seconds (cached).

---

## 🔍 Step 2 — Upscale

Upload your image(s) and the AI enhances them.

### Settings

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Scale** | 2x, 4x | 4x | How much to enlarge |
| **Model** | general, anime | general | General for photos, anime for illustrations |
| **Output** | png, jpg, webp | png | Output format |
| **Face Enhance** | on/off | off | GFPGAN for portraits |

### Tips
- **Photos**: Use `general` model
- **Anime/illustrations**: Use `anime` model
- **Portraits**: Enable `face_enhance`
- **Large images**: May take longer; tile mode handles low VRAM automatically

---

## 💾 Step 3 — Export

Download all upscaled images as a zip. Optional cleanup to free disk space.

---

## 🎛️ All Settings Explained

### Scale Factor

| Scale | Output Size | Best For |
|-------|------------|----------|
| **2x** | 2× original | Moderate enhancement, faster |
| **4x** | 4× original | Maximum quality, default |

### Model Type

| Model | Best For | Size |
|-------|----------|------|
| **General** | Photos, real-world images | ~65 MB |
| **Anime** | Illustrations, anime, drawings | ~18 MB |

### Output Format

| Format | Quality | Size | Best For |
|--------|---------|------|----------|
| **PNG** | Lossless | Large | Archival, editing |
| **JPG** | 95% | Small | Sharing, web |
| **WEBP** | 95% | Smallest | Web, modern apps |

---

## ❓ FAQ

**Q: How big can the input image be?**
A: Limited by GPU VRAM. T4 (16 GB) handles most images. Very large images auto-switch to tile mode.

**Q: Can I upscale multiple images at once?**
A: Yes! Upload multiple files in Step 2 — they're processed sequentially.

**Q: Does it cost money?**
A: No. Runs on Google Colab's free T4 GPU.

**Q: What about video upscaling?**
A: Not supported yet. Extract frames, upscale individually, reassemble.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `CUDA out of memory` | Smaller input image, or restart runtime |
| `Model not found` | Re-run Step 1 |
| `No GPU detected` | Runtime → Change runtime type → T4 |
| `Download failed` | Check internet, re-run Step 1 |
