from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FakeResponse:
    data: list[dict[str, Any]]
    error: Any = None


class FakeTable:
    def __init__(self, client: "FakeSupabase", name: str) -> None:
        self._client = client
        self._name = name
        self._action = None
        self._columns: list[str] | None = None
        self._payload: list[dict[str, Any]] | None = None
        self._filter_in: tuple[str, set[Any]] | None = None
        self._filter_eq: tuple[str, Any] | None = None
        self._filter_neq: tuple[str, Any] | None = None
        self._updates: dict[str, Any] | None = None

    def select(self, columns: str) -> "FakeTable":
        self._action = "select"
        if columns == "*":
            self._columns = None
        else:
            self._columns = [col.strip() for col in columns.split(",")]
        return self

    def order(self, _: str) -> "FakeTable":
        return self

    def insert(self, payload: list[dict[str, Any]]) -> "FakeTable":
        self._action = "insert"
        self._payload = payload
        return self

    def upsert(self, payload: list[dict[str, Any]], on_conflict: str | None = None) -> "FakeTable":
        self._action = "upsert"
        self._payload = payload
        if on_conflict:
            self._client._conflict_key = on_conflict
        return self

    def delete(self) -> "FakeTable":
        self._action = "delete"
        return self

    def update(self, updates: dict[str, Any]) -> "FakeTable":
        self._action = "update"
        self._updates = updates
        return self

    def eq(self, column: str, value: Any) -> "FakeTable":
        self._filter_eq = (column, value)
        return self

    def in_(self, column: str, values: list[Any]) -> "FakeTable":
        self._filter_in = (column, set(values))
        return self

    def neq(self, column: str, value: Any) -> "FakeTable":
        self._filter_neq = (column, value)
        return self

    def _matches_filters(self, row: dict[str, Any]) -> bool:
        if self._filter_eq:
            column, value = self._filter_eq
            return row.get(column) == value
        if self._filter_in:
            column, values = self._filter_in
            return row.get(column) in values
        if self._filter_neq:
            column, value = self._filter_neq
            return row.get(column) != value
        return True

    def execute(self) -> FakeResponse:
        table = self._client._tables.setdefault(self._name, [])
        if self._action == "select":
            rows = [row.copy() for row in table]
            if self._columns is not None:
                rows = [
                    {col: row.get(col) for col in self._columns}
                    for row in rows
                ]
            return FakeResponse(rows)

        if self._action == "insert":
            inserted = []
            for row in self._payload or []:
                record = row.copy()
                record.setdefault("id", self._client._next_id(self._name))
                table.append(record)
                inserted.append(record)
            return FakeResponse(inserted)

        if self._action == "upsert":
            inserted = []
            key = getattr(self._client, "_conflict_key", None)
            for row in self._payload or []:
                record = row.copy()
                if key:
                    existing = next((r for r in table if r.get(key) == record.get(key)), None)
                    if existing:
                        existing.update(record)
                        inserted.append(existing.copy())
                        continue
                record.setdefault("id", self._client._next_id(self._name))
                table.append(record)
                inserted.append(record)
            return FakeResponse(inserted)

        if self._action == "update":
            updated: list[dict[str, Any]] = []
            for row in table:
                if self._matches_filters(row):
                    row.update(self._updates or {})
                    updated.append(row.copy())
            return FakeResponse(updated)

        if self._action == "delete":
            original = list(table)
            remaining = [row for row in original if not self._matches_filters(row)]
            deleted = [row for row in original if row not in remaining]
            self._client._tables[self._name] = remaining
            return FakeResponse(deleted)

        return FakeResponse([])


class FakeSupabase:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] = {}
        self._id_counters: dict[str, int] = {}
        self._conflict_key: str | None = None

    def _next_id(self, table: str) -> int:
        self._id_counters.setdefault(table, 1)
        value = self._id_counters[table]
        self._id_counters[table] += 1
        return value

    def table(self, name: str) -> FakeTable:
        return FakeTable(self, name)
