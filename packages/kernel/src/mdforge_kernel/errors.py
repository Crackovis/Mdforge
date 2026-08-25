from __future__ import annotations

from mdforge_contracts import StructuredError


class RuntimeIssue(Exception):
    def __init__(self, error: StructuredError) -> None:
        self.error = error
        super().__init__(error.message)


class RuntimeActivationError(RuntimeIssue):
    def __init__(
        self,
        error: StructuredError,
        rollback_errors: tuple[StructuredError, ...] = (),
    ) -> None:
        self.rollback_errors = rollback_errors
        super().__init__(error)


class RuntimeShutdownError(RuntimeIssue):
    def __init__(self, error: StructuredError, stop_errors: tuple[StructuredError, ...]) -> None:
        self.stop_errors = stop_errors
        super().__init__(error)
