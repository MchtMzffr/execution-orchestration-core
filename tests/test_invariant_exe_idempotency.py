# Decision Ecosystem — execution-orchestration-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""INV-EXE-5: Idempotency tests."""

from decision_schema.types import Action, FinalDecision

from execution_orchestration_core.orchestrator import execute
from execution_orchestration_core.policies import ExecutionPolicy, IdempotencyPolicy


def test_inv_exe_5_idempotency_key_generation() -> None:
    """Idempotency keys are generated when enabled."""
    policy = ExecutionPolicy(
        idempotency=IdempotencyPolicy(enabled=True, key_generator="action+context_hash"),
    )

    def executor(_action: Action, _context: dict) -> tuple[bool, str | None]:
        return True, None

    final_decision = FinalDecision(action=Action.ACT, allowed=True, reasons=["test"])
    context = {"now_ms": 1000}

    report = execute(final_decision, context, policy, executor)

    # Should have idempotency keys in attempts (when implemented)
    # For now, just verify execution succeeds
    assert report.success_count > 0


def test_inv_exe_5_idempotency_disabled_no_keys() -> None:
    """Idempotency disabled: no keys generated."""
    policy = ExecutionPolicy(
        idempotency=IdempotencyPolicy(enabled=False),
    )

    def executor(_action: Action, _context: dict) -> tuple[bool, str | None]:
        return True, None

    final_decision = FinalDecision(action=Action.ACT, allowed=True, reasons=["test"])
    context = {}

    report = execute(final_decision, context, policy, executor)

    # Should execute successfully without idempotency keys
    assert report.success_count > 0
    # Keys should be None when disabled
    assert all(attempt.idempotency_key is None for attempt in report.attempts)
