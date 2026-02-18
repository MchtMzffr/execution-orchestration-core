# Decision Ecosystem — execution-orchestration-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Execution orchestration data models."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from decision_schema.types import Action, FinalDecision


class ExecutionStatus(str, Enum):
    """Execution attempt status (INV-EXE-1)."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    DENIED = "denied"


@dataclass
class ExecutionAttempt:
    """Single execution attempt result (INV-EXE-SEC-1: no raw message in serializable surface)."""

    action: Action
    status: ExecutionStatus
    attempt_number: int
    latency_ms: int
    error_type: str | None = None  # e.g. type(e).__name__ or "executor_rejected"
    error_code: str | None = None  # e.g. "executor_failed", "timeout", "execution_exception"
    error_message: str | None = None  # deprecated: do not set; use error_type/error_code
    idempotency_key: str | None = None


@dataclass
class ExecutionPlan:
    """Execution plan for FinalDecision actions."""

    actions: list[Action]
    max_retries: int
    max_total_time_ms: int
    timeout_per_action_ms: int
    idempotency_enabled: bool = False


@dataclass
class ExecutionReport:
    """Execution report for PacketV2 trace extension."""

    attempts: list[ExecutionAttempt] = field(default_factory=list)
    total_latency_ms: int = 0
    success_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    denied_count: int = 0
    fail_closed: bool = False

    def to_external_dict(self) -> dict[str, Any]:
        """
        Convert to PacketV2.external dict (trace extension keys).
        
        Keys follow INV-T1 format: exec.* namespace.
        """
        return {
            "exec.total_latency_ms": self.total_latency_ms,
            "exec.success_count": self.success_count,
            "exec.failed_count": self.failed_count,
            "exec.skipped_count": self.skipped_count,
            "exec.denied_count": self.denied_count,
            "exec.fail_closed": self.fail_closed,
            "exec.attempt_count": len(self.attempts),
        }
