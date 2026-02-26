# CLI Entrypoint Design (2026-02-25)

## Summary
Add a Python package entrypoint so the CLI can be run as `lmt` after installation.

## Goals
- Provide `lmt` console script mapping to `localmeetingtranscriber.main:main`.
- Use modern packaging via `pyproject.toml`.
- Keep existing `requirements.txt` for convenience.

## Non-Goals
- Remove `requirements.txt`.
- Add additional build tooling or publishing steps.

## Approach
Use `pyproject.toml` with setuptools and a `project.scripts` entry:
`lmt = "localmeetingtranscriber.main:main"`.

## Files
- Create: `pyproject.toml`
- Modify: `README.md` (add install/run example for `lmt`)
