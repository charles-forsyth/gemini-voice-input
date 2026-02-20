# Design Document: Troubleshooting Paste Functionality

## 1. Project Overview & Mission
**Mission:** Troubleshoot and resolve the issue where the paste functionality is broken ("nothing happens when pasting") in the `gemini-voice-input` project.

## 2. Language Selection & Architecture
*   **Language:** Python >= 3.12
*   **Package Manager:** `uv`
*   **Project Layout:** Standard `src/` layout (e.g., `src/gemini_voice_input/`)
*   **Configuration:** `pyproject.toml`
*   **Core Libraries:**
    *   **System Integration:** `wl-clipboard` / `xclip` (for clipboard operations), `xdotool` or `ydotool` (if simulated keypresses are used for pasting).

## 3. Toolchain Definition
The following tools will be leveraged for development and debugging:
*   **Dependency Management & Execution:** `uv`
*   **Linter & Formatter:** `ruff` (run via `uv run ruff check .` and `uv run ruff format .`)
*   **Type Checker:** `mypy` (run via `uv run mypy src`)
*   **Testing Framework:** `pytest` (run via `uv run pytest`)

## 4. Troubleshooting Strategy
1.  **Clipboard Validation:**
    *   Verify if the transcribed text is successfully copied to the system clipboard using the expected utility (`wl-copy` for Wayland or `xclip` for X11).
    *   Log the exact text being sent to the clipboard to ensure it is not empty.
2.  **Paste Mechanism Investigation:**
    *   Determine how the application is attempting to paste the text (e.g., relying solely on clipboard copy for manual paste, or attempting an automated keypress simulation like `Ctrl+V` or `Shift+Insert`).
    *   If automated pasting is implemented via keyboard simulation (e.g., `xdotool`, `ydotool`, `wtype`), verify that the simulation utility is installed, accessible, and compatible with the current display server (X11 vs. Wayland).
3.  **Environment Check:**
    *   Identify if the user is running a Wayland or X11 session (`echo $XDG_SESSION_TYPE`), as clipboard and input simulation methods differ significantly between the two.
4.  **Logging and Error Handling:**
    *   Add robust logging or notifications (`notify-send`) around the clipboard interaction points to capture any subprocess execution failures or silent errors.

## 5. Documentation Updates
*   **`README.md`:** Must be updated with clear prerequisites regarding clipboard utilities (e.g., ensuring `wl-clipboard` or `xclip` are installed) and any required input simulation tools.
*   **Code Comments:** Document the findings and the specific fixes implemented to restore the paste functionality.

## 6. CI/CD (GitHub Actions)
The CI/CD pipeline will ensure the Python codebase remains healthy while debugging system-level integrations.

```yaml
name: CI

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

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

      - name: Lint with Ruff
        run: uv run ruff check .

      - name: Format Check with Ruff
        run: uv run ruff format --check .

      - name: Type Check with Mypy
        run: uv run mypy src

      - name: Run Tests
        run: uv run pytest
```
