import pytest

from app.core.exceptions import ReadOnlyViolationError
from app.db.mssql import guard_read_only


def test_guard_read_only_blocks_destructive_queries():
    blocked_queries = [
        "INSERT INTO users (name) VALUES ('alice')",
        "UPDATE users SET name = 'bob'",
        "DELETE FROM users WHERE id = 1",
        "DROP TABLE users",
        "ALTER TABLE users ADD COLUMN age INT",
        "TRUNCATE TABLE logs",
        "CREATE TABLE test (id INT)",
        "MERGE INTO target USING source ON target.id = source.id",
    ]
    for q in blocked_queries:
        with pytest.raises(ReadOnlyViolationError):
            guard_read_only(q)


def test_guard_read_only_allows_selects():
    allowed_queries = [
        "SELECT 1",
        "SELECT * FROM sys.tables",
        "SELECT s.name, t.name FROM sys.tables t JOIN sys.schemas s ON t.schema_id = s.schema_id",
        "WITH CTE AS (SELECT 1 AS n) SELECT * FROM CTE",
        "SELECT TOP (100) [Update], [DeleteDate], [CreateTime] FROM [dbo].[users]",
    ]
    for q in allowed_queries:
        # Should not raise
        guard_read_only(q)
