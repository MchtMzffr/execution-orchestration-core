"""INV-EXE-3: Fail-closed behavior tests."""

import pytest
from decision_schema.types import Action, FinalDecision

from execution_orchestration_core.model import ExecutionReport, ExecutionStatus
from execution_orchestration_core.orchestrator import ActionExecutor, execute
from execution_orchestration_core.policies import ExecutionPolicy


def test_inv_exe_3_exception_sets_fail_closed() -> None:
    """Exception in executor sets fail_closed marker."""
    policy = ExecutionPolicy()

    def exception_executor(_action: Action, _context: dict) -> tuple[bool, str | None]:
        raise RuntimeError("injected exception")

    final_decision = FinalDecision(action=Action.ACT, allowed=True, reasons=["test"])
    context = {}

    report = execute(final_decision, context, policy, exception_executor)

    # Should have fail_closed marker
    assert report.fail_closed is True
    assert report.failed_count > 0
    assert any(attempt.status == ExecutionStatus.FAILED for attempt in report.attempts)


def test_inv_exe_3_timeout_sets_fail_closed() -> None:
    """Timeout exceeding max_total_time_ms sets fail_closed."""
    policy = ExecutionPolicy(
        retry=ExecutionPolicy().retry,
        timeout=ExecutionPolicy().timeout,
    )
    policy.timeout.max_total_time_ms = 50  # Very short

    def slow_executor(_action: Action, _context: dict) -> tuple[bool, str | None]:
        import time

        time.sleep(0.1)  # 100ms
        return False, "slow"

    final_decision = FinalDecision(action=Action.ACT, allowed=True, reasons=["test"])
    context = {}

    report = execute(final_decision, context, policy, slow_executor)

    # Should have fail_closed due to timeout
    assert report.fail_closed is True
