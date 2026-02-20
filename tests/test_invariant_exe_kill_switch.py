# Decision Ecosystem — execution-orchestration-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""INV-EXE-4: Kill-switch compliance tests."""

from decision_schema.types import Action, FinalDecision

from execution_orchestration_core.orchestrator import execute
from execution_orchestration_core.policies import ExecutionPolicy


def test_inv_exe_4_kill_switch_denies_execution() -> None:
    """Kill-switch active (ops_deny_actions=True) denies execution."""
    policy = ExecutionPolicy()

    def executor(_action: Action, _context: dict) -> tuple[bool, str | None]:
        return True, None  # Would succeed normally

    final_decision = FinalDecision(action=Action.ACT, allowed=True, reasons=["test"])
    context = {"ops_deny_actions": True}  # Kill-switch active

    report = execute(final_decision, context, policy, executor)

    # Should be denied (no attempts)
    assert report.denied_count == 1
    assert len(report.attempts) == 0
    assert report.fail_closed is False  # Not fail-closed, intentional deny


def test_inv_exe_4_final_decision_not_allowed_skips() -> None:
    """FinalDecision.allowed=False skips execution."""
    policy = ExecutionPolicy()

    def executor(_action: Action, _context: dict) -> tuple[bool, str | None]:
        return True, None

    final_decision = FinalDecision(action=Action.HOLD, allowed=False, reasons=["guard_triggered"])
    context = {}

    report = execute(final_decision, context, policy, executor)

    # Should be skipped (no attempts)
    assert report.skipped_count == 1
    assert len(report.attempts) == 0
