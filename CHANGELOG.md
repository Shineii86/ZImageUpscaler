# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.0.0] - 2026-05-17

### Added
- Initial release of Z-Image Upscaler
- Modular `src/` package: config, downloader, upscaler, exporter
- `src/config.py` — all constants, model URLs, defaults, scale presets
- `src/downloader.py` — aria2c-powered model downloader with Google Drive caching
- `src/upscaler.py` — Real-ESRGAN upscaler with 2x/4x support, face enhancement
- `src/exporter.py` — zip output and Colab browser download
- `notebook/ZImageUpscaler.ipynb` — 3-cell Colab notebook with inline-styled UI
- Real-ESRGAN x4plus general model (~65 MB)
- Real-ESRGAN x4plus anime model (~18 MB)
- GFPGAN face enhancement integration
- Tile mode fallback for low VRAM
- Half-precision (FP16) on supported GPUs
- Theme-safe inline-styled UI (works in both Colab dark/light modes)
- `README.md` — comprehensive documentation with architecture, badges, FAQ
- `CHANGELOG.md` — version history tracking
- `CONTRIBUTING.md` — contribution guidelines
- `GUIDE.md` — beginner-friendly user guide
- `SECURITY.md` — vulnerability reporting policy
- `.github/ISSUE_TEMPLATE/` — bug report and feature request templates
- `.github/PULL_REQUEST_TEMPLATE.md` — PR checklist
- `.gitignore` — Python, Jupyter, model files, OS artifacts
- `requirements.txt` — core ML dependencies
- `LICENSE` — MIT license
