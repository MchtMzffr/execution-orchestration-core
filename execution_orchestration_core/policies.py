"""Execution policies: retry, backoff, timeout, idempotency."""

from dataclasses import dataclass


@dataclass
class RetryPolicy:
    """Retry policy for execution attempts."""

    max_retries: int = 3
    initial_backoff_ms: int = 100
    max_backoff_ms: int = 5000
    backoff_multiplier: float = 2.0

    def backoff_ms(self, attempt_number: int) -> int:
        """
        Compute backoff delay for attempt number (exponential backoff).
        
        Args:
            attempt_number: 0-indexed attempt number (0 = first attempt)
        
        Returns:
            Backoff delay in milliseconds
        """
        if attempt_number == 0:
            return 0
        delay = self.initial_backoff_ms * (self.backoff_multiplier ** (attempt_number - 1))
        return min(int(delay), self.max_backoff_ms)


@dataclass
class TimeoutPolicy:
    """Timeout policy for execution."""

    timeout_per_action_ms: int = 5000
    max_total_time_ms: int = 30000


@dataclass
class IdempotencyPolicy:
    """Idempotency policy for execution."""

    enabled: bool = False
    key_generator: str | None = None  # "action+context_hash", "custom", etc.


@dataclass
class ExecutionPolicy:
    """Complete execution policy (INV-EXE-2: boundedness)."""

    retry: RetryPolicy = field(default_factory=RetryPolicy)
    timeout: TimeoutPolicy = field(default_factory=TimeoutPolicy)
    idempotency: IdempotencyPolicy = field(default_factory=IdempotencyPolicy)
    max_concurrency: int = 1  # Sequential execution by default
