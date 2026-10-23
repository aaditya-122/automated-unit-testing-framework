"""Thirty-five named cases covering CRUD, boundaries, and invalid input."""
import pytest
from qa_crud import ValidationError

CASES = []
def add(case_id, operation, args, expected, severity="medium"):
    CASES.append(pytest.param(operation, args, expected, id=case_id, marks=pytest.mark.case(
        id=case_id, input=f"{operation}{args!r}", expected=str(expected), severity=severity)))

for i in range(8):
    add(f"create-valid-{i+1:02}", "create", (f"User {i}", f"u{i}@example.com"), "created user")
for i, (name, email) in enumerate([
    ("", "x@example.com"), ("   ", "x@example.com"), (None, "x@example.com"),
    ("A"*101, "x@example.com"), ("Valid", ""), ("Valid", "missing-at"),
    ("Valid", "@example.com"), ("Valid", "x@localhost"), ("Valid", "x"*250+"@a.com")]):
    add(f"create-invalid-{i+1:02}", "create", (name, email), ValidationError, "high")
for value in [0, -1, 1001, 1.5, True, "10"]:
    add(f"list-invalid-{str(value).replace(' ','')}", "list", (value,), ValidationError, "medium")
for value in [1, 10, 100, 1000]:
    add(f"list-boundary-{value}", "list", (value,), "list")
add("get-missing", "get", (987654,), LookupError, "high")
add("update-missing", "update", (987654, "Name", "n@example.com"), LookupError, "high")
add("delete-missing", "delete", (987654,), LookupError, "medium")
add("create-duplicate-email", "duplicate", (), ValidationError, "high")
add("update-existing", "update_existing", (), "updated user")
add("delete-existing", "delete_existing", (), "deleted user")
add("case-insensitive-duplicate", "case_duplicate", (), ValidationError, "high")

@pytest.mark.parametrize("operation,args,expected", CASES)
def test_repository_case(repo, operation, args, expected):
    if operation == "duplicate":
        repo.create("First", "same@example.com")
        with pytest.raises(expected):
            repo.create("Second", "same@example.com")
        return
    if operation == "case_duplicate":
        repo.create("First", "same@example.com")
        with pytest.raises(expected):
            repo.create("Second", "SAME@example.com")
        return
    if operation == "update_existing":
        user = repo.create("Before", "before@example.com")
        changed = repo.update(user["id"], "After", "after@example.com")
        assert changed["name"] == "After" and changed["email"] == "after@example.com"
        return
    if operation == "delete_existing":
        user = repo.create("Delete", "delete@example.com")
        repo.delete(user["id"])
        with pytest.raises(LookupError):
            repo.get(user["id"])
        return
    if expected in (ValidationError, LookupError):
        with pytest.raises(expected):
            getattr(repo, operation)(*args)
    elif operation == "create":
        created = repo.create(*args)
        assert created["name"] == args[0].strip()
        assert created["email"] == args[1].strip().lower()
    else:
        assert repo.list(*args) == []
