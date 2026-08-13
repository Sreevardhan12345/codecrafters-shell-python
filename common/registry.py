"""A tiny registry used for builtin command registration."""

from collections.abc import Callable, Iterator
from typing import TypeVar


T = TypeVar("T")


class Registry:
    """Map normalized names to callables without exposing mutable storage."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._entries: dict[str, T] = {}

    def register(self, key: str) -> Callable[[T], T]:
        """Register an item, failing early when a name is registered twice."""
        normalized_key = key.upper()

        def decorator(item: T) -> T:
            if normalized_key in self._entries:
                raise KeyError(f"{normalized_key!r} already registered in {self.name!r}")
            self._entries[normalized_key] = item
            return item

        return decorator

    def get(self, key: str) -> T:
        """Return an item by name."""
        return self._entries[key.upper()]

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key.upper() in self._entries

    def __iter__(self) -> Iterator[str]:
        return iter(self._entries)
