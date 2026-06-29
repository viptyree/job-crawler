# Errors

Command failures and integration errors.

---

## [ERR-20260629-005] command_failure

**Logged**: 2026-06-29T17:00:00+08:00
**Priority**: low
**Status**: resolved
**Command**: Restart backend process on port 8000
**Area**: tooling

### Symptoms
PowerShell failed with `Cannot overwrite variable PID because it is read-only or constant`.

### Root Cause
PowerShell variable names are case-insensitive, so `$pid` conflicts with the built-in `$PID`.

### Fix
Use a different variable name such as `$backendPid`.

### Prevention
Avoid `$pid` as a local variable name in PowerShell scripts.

### Metadata
- Related Files: none
- Tags: powershell, process

---

## [ERR-20260629-004] command_failure

**Logged**: 2026-06-29T17:00:00+08:00
**Priority**: medium
**Status**: resolved
**Command**: pnpm install
**Area**: install

### Symptoms
`pnpm install` completed package installation but exited with `ERR_PNPM_IGNORED_BUILDS`.

### Root Cause
The installed pnpm version requires explicit approval for dependency build scripts such as `esbuild`.

### Fix
Run `pnpm approve-builds --all`, then rerun `pnpm build`.

### Prevention
Document pnpm 11 build script approval behavior for fresh Windows installs.

### Metadata
- Related Files: frontend/package.json
- Tags: pnpm, frontend

---

## [ERR-20260629-002] command_failure

**Logged**: 2026-06-29T17:00:00+08:00
**Priority**: medium
**Status**: resolved
**Command**: Backend service smoke test
**Area**: install

### Symptoms
Python failed with `ModuleNotFoundError: No module named 'sqlalchemy'`.

### Root Cause
The active Python environment did not have the project's existing `backend/requirements.txt` installed.

### Fix
Install existing backend dependencies with `pip install -r requirements.txt`.

### Prevention
Run dependency installation before backend runtime smoke tests in a fresh workspace.

### Metadata
- Related Files: backend/requirements.txt
- Tags: python, dependencies

---

## [ERR-20260629-003] command_failure

**Logged**: 2026-06-29T17:00:00+08:00
**Priority**: low
**Status**: resolved
**Command**: FastAPI route list smoke test
**Area**: tests

### Symptoms
Route inspection failed with `AttributeError: '_IncludedRouter' object has no attribute 'path'`.

### Root Cause
The quick inspection assumed every `app.routes` item exposes `path`.

### Fix
Use `getattr(route, 'path', '')` while filtering route objects.

### Prevention
When inspecting framework internals in smoke tests, guard optional attributes.

### Metadata
- Related Files: backend/app/main.py
- Tags: fastapi, smoke-test

---

## [ERR-20260629-001] command_failure

**Logged**: 2026-06-29T17:00:00+08:00
**Priority**: low
**Status**: resolved
**Command**: Python inline smoke test with Bash here-doc syntax
**Area**: tooling

### Symptoms
PowerShell returned `Missing file specification after redirection operator`.

### Root Cause
The command used Bash `python - <<'PY'` syntax while the workspace shell is PowerShell.

### Fix
Use `python -c` or a PowerShell here-string piped to `python -` on Windows.

### Prevention
Check the active shell before writing inline scripts and prefer `python -c` for short smoke tests.

### Metadata
- Related Files: none
- Tags: powershell, smoke-test

---
