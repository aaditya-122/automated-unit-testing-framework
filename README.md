# Automated Unit Testing & Test Case Documentation Framework

A Python CRUD example plus a reusable pytest suite and report plugin. Annotated tests are exported to CSV and Markdown with test ID, input, expected/actual result, status, and severity.

## Features
- SQLite CRUD repository with input constraints.
- 30+ functional, boundary, and negative-input tests.
- `@pytest.mark.case` metadata and a pytest hook for documentation reports.
- Coverage gate configured at 90% and GitHub Actions workflow.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest --cov=qa_crud --cov-report=term-missing
```
Reports are written to `reports/test-cases.csv` and `reports/test-cases.md`. Set `TEST_REPORT_DIR` to change the destination.

## Extend
Implement behavior in `src/qa_crud/repository.py`, add tests under `tests/`, and apply `@pytest.mark.case(id=..., input=..., expected=..., severity=...)` to include tests in the generated documentation.

The database is an isolated in-memory SQLite connection per test. Reports capture pytest's observed outcome and failure detail. See `LICENSE` for licensing.
