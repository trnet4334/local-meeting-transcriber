# CLI Entrypoint Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `pyproject.toml` that exposes the CLI as `lmt`.

**Architecture:** Use setuptools in `pyproject.toml` with a `project.scripts` entry pointing to `localmeetingtranscriber.main:main` and update README usage.

**Tech Stack:** Python 3.11, setuptools.

---

### Task 1: Add pyproject and update README

**Files:**
- Create: `pyproject.toml`
- Modify: `README.md`
- Test: `tests/test_cli_helpers.py`

**Step 1: Write the failing test**

```python
def test_console_script_name():
    import tomllib
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["scripts"]["lmt"] == "localmeetingtranscriber.main:main"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_helpers.py::test_console_script_name -v`
Expected: FAIL (file missing or key missing)

**Step 3: Write minimal implementation**

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "localmeetingtranscriber"
version = "0.1.0"
description = "CLI to transcribe local meeting recordings"
requires-python = ">=3.11"
dependencies = ["python-docx>=1.1.0"]

[project.scripts]
lmt = "localmeetingtranscriber.main:main"
```

Update README usage section to mention:
```
pip install -e .
lmt
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_helpers.py::test_console_script_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml README.md tests/test_cli_helpers.py
git commit -m "feat: add lmt console entrypoint"
```
