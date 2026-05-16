# Contributing to Z-Image Upscaler

Thank you for your interest in contributing!

---

## Ways to Contribute

### 🐛 Report Bugs
[Open an Issue](https://github.com/Shineii86/ZImageUpscaler/issues) with steps to reproduce, expected vs actual behavior, and your environment.

### 💡 Suggest Features
[Start a Discussion](https://github.com/Shineii86/ZImageUpscaler/issues) with what problem it solves and how it should work.

### 🔀 Submit Code
1. **Fork** the repository
2. **Clone**: `git clone https://github.com/YOUR_USERNAME/ZImageUpscaler.git`
3. **Branch**: `git checkout -b feature/your-feature`
4. **Make changes** and test in Colab
5. **Commit**: `git commit -m "feat: description"`
6. **Push** and open a **Pull Request**

---

## Development Setup

```bash
git clone https://github.com/Shineii86/ZImageUpscaler.git
cd ZImageUpscaler
pip install -r requirements.txt
```

## Code Style

- Follow existing `src/` module patterns
- Use shared `log` from `src/__init__.py`
- Add `@param` and `@returns` docstrings
- Add `# ---- FEATURE: name ----` section markers
- Keep `__all__` exports updated
- Update `CHANGELOG.md` with every change (newest at top)

## Commit Messages

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `refactor:` — code restructure
