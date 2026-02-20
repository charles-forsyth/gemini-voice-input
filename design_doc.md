# Design Document: Troubleshooting & Repair

## 1. Project Overview & Mission
**Mission:** Troubleshoot and repair the broken state of the `gemini-voice-input` project. The application currently fails to function correctly, requiring systematic debugging and resolution to restore core features (voice recording, transcription, and clipboard integration).

## 2. Language Selection & Architecture
*   **Language:** Python >= 3.12
*   **Package Manager:** `uv`
*   **Project Layout:** Standard `src/` layout (e.g., `src/gemini_voice_input/`)
*   **Configuration:** `pyproject.toml`
*   **Core Libraries:**
    *   **Audio:** `sounddevice`, `numpy`, `scipy`
    *   **Transcription:** `google-cloud-speech` (Cloud Speech-to-Text v2 API - Chirp 3 model) or `google-genai` (depending on the broken component)
    *   **System Integration:** Bash, `wl-clipboard` / `xclip`, `notify-send`, `paplay`

## 3. Toolchain Definition
The following tools will be leveraged to systematically identify and fix the issues:
*   **Dependency Management & Execution:** `uv`
*   **Linter & Formatter:** `ruff`
*   **Type Checker:** `mypy`
*   **Testing Framework:** `pytest`

## 4. Troubleshooting Strategy
1.  **Environment & Dependency Verification:**
    *   Ensure all dependencies in `pyproject.toml` and `uv.lock` are correctly resolved using `uv sync`.
    *   Verify the Python version (`>= 3.12`).
2.  **Authentication & Configuration Check:**
    *   Validate Google Cloud Application Default Credentials (`gcloud auth application-default login`) or API key configuration, depending on the active transcription engine.
3.  **Component Isolation Testing:**
    *   **Audio Capture:** Test `sounddevice` recording and WAV file generation independently.
    *   **Transcription API:** Verify the Google Cloud API calls for authentication, request formatting, and response parsing.
    *   **Clipboard Integration:** Ensure `wl-copy` or `xclip` are functioning as expected within the target environment (Wayland vs. X11).
4.  **Static Analysis & Testing:**
    *   Run `uv run ruff check .` to identify syntax errors or unused imports.
    *   Run `uv run mypy src` to catch any typing inconsistencies.
    *   Execute the existing test suite via `uv run pytest` to pinpoint failing components.

## 5. Documentation
*   **`README.md`:** Must be updated with any findings from the troubleshooting process, particularly if environmental setup steps, authentication procedures, or dependency requirements change as a result of the fixes.
*   **Inline Comments:** Document the root cause of the bug and the implemented fix within the code for future reference.

## 6. CI/CD (GitHub Actions)
The CI/CD pipeline ensures that the fixes are robust and no further regressions are introduced. The `.github/workflows/ci.yml` will be enforced as follows:

```yaml
name: CI

on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Dependencies
        run: uv sync --all-extras --dev

      - name: Lint (Ruff)
        run: uv run ruff check .

      - name: Format Check (Ruff)
        run: uv run ruff format --check .

      - name: Type Check (Mypy)
        run: uv run mypy src

      - name: Run Tests (Pytest)
        run: uv run pytest
```
