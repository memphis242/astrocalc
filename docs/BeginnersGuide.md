# Beginner's Guide

## Build Systems and Hatchling (What `[build-system]` Does)

In `pyproject.toml`, the `[build-system]` section tells Python tooling which backend to use to build your package.

Example:

```toml
[build-system]
requires = ["hatchling>=1.0"]
build-backend = "hatchling.build"
```

- `requires`: tools needed in an isolated build environment.
- `build-backend`: the implementation that performs the build (PEP 517 backend).

With Hatchling, build tools such as `pip` or `python -m build` can create:
- A source distribution (`sdist`, `.tar.gz`)
- A wheel (`.whl`) for installation

For CLI apps, define an entrypoint so install creates a runnable command:

```toml
[project.scripts]
astrocalc = "astrocalc.cli:astrocalc"
```

This maps shell command `astrocalc` to the Click root function in `astrocalc/cli.py`.

## Packaging for Distribution

You distribute Python packages primarily as:
- `wheel`: built artifact for fast installation
- `sdist`: source artifact for compatibility and fallback builds

The normal package output directory is `dist/`.

Install a built wheel locally:

```bash
python -m pip install dist/astrocalc-0.1.0-py3-none-any.whl
```

Reinstall while testing:

```bash
python -m pip install --force-reinstall dist/astrocalc-0.1.0-py3-none-any.whl
```

## Typical Release Workflow (Build -> TestPyPI -> Verify -> PyPI)

1. Build artifacts:

```bash
python -m build
```

2. Upload to TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

3. Test install from TestPyPI in a clean virtual environment:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ astrocalc
```

4. Smoke test command behavior:

```bash
astrocalc --help
```

5. Upload the same validated artifacts to PyPI:

```bash
python -m twine upload dist/*
```

Notes:
- Use API tokens for auth (recommended).
- `twine` is the classic uploader, but CI trusted publishing and tool-specific publishers (for example, Hatch) are also common.

## CI Setup for Auto-Publish on Merge to `main`

High-level recommendation:

1. Use CI on pull requests for quality checks only:
- run tests
- run lint/type checks
- optionally build package to verify it can be built

2. Use a protected release workflow on merge to `main`:
- gate on successful checks
- build once in CI (`python -m build`)
- publish with:
  - preferred: trusted publishing (OIDC) to PyPI
  - fallback: PyPI API token stored in CI secrets

3. Add release safety controls:
- publish only on version change or tag
- fail if version already exists on PyPI
- keep build and publish logs/audit trail

Practical pattern:
- PR merge to `main` creates a tag or bump commit
- release job runs from that immutable ref
- release job publishes artifacts

This reduces accidental releases and keeps provenance clear.

## Private PyPI Registry (High-Level)

A private package registry is useful for internal tools or closed-source libraries.

Common options:
- Self-hosted: `devpi`, `pypiserver`
- Repository managers: Sonatype Nexus, JFrog Artifactory
- Cloud registries: AWS CodeArtifact, Google Artifact Registry, Azure Artifacts

Typical setup shape:

1. Stand up registry and access control:
- org/user accounts
- read/write permissions by team or project

2. Configure publishing credentials in CI:
- upload internal package versions to private index

3. Configure installers (`pip`) to use private index:
- `--index-url` for private-only
- `--extra-index-url` if mixing public PyPI and private

4. Decide dependency policy:
- mirror/caching strategy for public packages
- allowlist/denylist and vulnerability scanning

5. Operational concerns:
- retention and cleanup policies
- backups and disaster recovery
- audit logs and token rotation

For many teams, the fastest path is a managed cloud registry plus CI publishing.
