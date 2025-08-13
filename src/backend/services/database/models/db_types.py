from __future__ import annotations

# Shared SQLAlchemy JSON TypeDecorator that preserves Unicode characters
# by delegating serialization to the dialect/driver and avoiding manual dumps.
# It also tolerates legacy rows where JSON columns accidentally store stringified
# JSON (e.g., "[\"中文\",\"测试\"]") by attempting json.loads on str values.
from sqlalchemy.types import TypeDecorator, JSON
import json


class UnicodePreservingJSON(TypeDecorator):
    """JSON column type that preserves non-ASCII characters.

    Bind phase:
      - Return Python objects directly (list/dict/etc.).
      - Avoid json.dumps here to prevent double-serialization and forced escaping.

    Result phase:
      - If value is already a Python list/dict, return as-is.
      - If value is a str (e.g., legacy data stored as a JSON string),
        attempt json.loads(value) to recover the original object; if it fails,
        return the string as-is.
    """

    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        # Simply return the value as-is for PostgreSQL JSONB to handle.
        # This avoids any unnecessary conversions that might escape Unicode.
        # PostgreSQL JSONB natively supports Unicode characters.
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, (list, dict)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                # If it's just a normal string (not JSON), return as-is
                return value
        return value

