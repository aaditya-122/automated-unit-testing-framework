"""A SQLite CRUD repository with explicit input constraints."""
import sqlite3
from typing import Any

class ValidationError(ValueError):
    """Raised when user data violates the repository contract."""

class UserRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK(length(trim(name)) BETWEEN 1 AND 100),
            email TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK(length(email) <= 254))""")
        self.connection.commit()

    @staticmethod
    def _validate(name: Any, email: Any) -> tuple[str, str]:
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("name must be a non-empty string")
        if len(name.strip()) > 100:
            raise ValidationError("name must be at most 100 characters")
        if not isinstance(email, str) or len(email) > 254 or "@" not in email:
            raise ValidationError("email must be a valid address of at most 254 characters")
        local, _, domain = email.partition("@")
        if not local or not domain or "." not in domain:
            raise ValidationError("email must contain a local part and dotted domain")
        return name.strip(), email.strip().lower()

    def create(self, name: str, email: str) -> dict[str, Any]:
        name, email = self._validate(name, email)
        try:
            cursor = self.connection.execute("INSERT INTO users(name,email) VALUES (?,?)", (name,email))
            self.connection.commit()
        except sqlite3.IntegrityError as exc:
            self.connection.rollback()
            raise ValidationError("email already exists") from exc
        return self.get(int(cursor.lastrowid))

    def get(self, user_id: int) -> dict[str, Any]:
        row = self.connection.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if row is None:
            raise LookupError(f"user {user_id} not found")
        return dict(row)

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 1000:
            raise ValidationError("limit must be an integer from 1 to 1000")
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM users ORDER BY id LIMIT ?", (limit,)).fetchall()]

    def update(self, user_id: int, name: str, email: str) -> dict[str, Any]:
        name, email = self._validate(name, email)
        try:
            cursor = self.connection.execute("UPDATE users SET name=?,email=? WHERE id=?", (name,email,user_id))
            if cursor.rowcount == 0:
                self.connection.rollback()
                raise LookupError(f"user {user_id} not found")
            self.connection.commit()
        except sqlite3.IntegrityError as exc:
            self.connection.rollback()
            raise ValidationError("email already exists") from exc
        return self.get(user_id)

    def delete(self, user_id: int) -> None:
        cursor = self.connection.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.connection.commit()
        if cursor.rowcount == 0:
            raise LookupError(f"user {user_id} not found")
