"""Pytest fixture and annotated case report exporter."""
import csv, os
from pathlib import Path
import pytest

@pytest.fixture
def repo():
    import sqlite3
    from qa_crud import UserRepository
    conn = sqlite3.connect(":memory:")
    yield UserRepository(conn)
    conn.close()

def pytest_configure(config):
    config._case_results = []

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    marker = item.get_closest_marker("case")
    if marker is None:
        return
    meta = marker.kwargs
    row = next((r for r in item.config._case_results if r["test_id"] == str(meta.get("id", item.name))), None)
    if row is None:
        row = {"test_id": str(meta.get("id", item.name)), "input": str(meta.get("input", "")),
               "expected_output": str(meta.get("expected", "")), "actual_output": "",
               "status": "", "severity": str(meta.get("severity", "medium"))}
        item.config._case_results.append(row)
    row["status"] = report.outcome.upper()
    row["actual_output"] = "PASS" if report.passed else str(report.longreprtext or report.outcome)

def pytest_sessionfinish(session, exitstatus):
    rows = session.config._case_results
    if not rows:
        return
    out = Path(os.getenv("TEST_REPORT_DIR", "reports"))
    out.mkdir(parents=True, exist_ok=True)
    fields = ["test_id", "input", "expected_output", "actual_output", "status", "severity"]
    with (out / "test-cases.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    lines = ["# Test Case Results", "", "| Test ID | Input | Expected Output | Actual Output | Status | Severity |", "|---|---|---|---|---|---|"]
    for row in rows:
        lines.append("| " + " | ".join(row[k].replace("|", "\\|").replace("\n", " ") for k in fields) + " |")
    (out / "test-cases.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
