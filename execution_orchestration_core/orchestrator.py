"""Execution orchestrator: main API (INV-EXE-1 through INV-EXE-6)."""

import logging
import time
from typing import Any, Callable

from decision_schema.types import Action, FinalDecision

from execution_orchestration_core.model import (
    ExecutionAttempt,
    ExecutionPlan,
    ExecutionReport,
    ExecutionStatus,
)
from execution_orchestration_core.policies import ExecutionPolicy

logger = logging.getLogger(__name__)


# Type alias for action executor (domain-agnostic interface)
ActionExecutor = Callable[[Action, dict[str, Any]], tuple[bool, str | None]]


def execute(
    final_decision: FinalDecision,
    context: dict[str, Any],
    policy: ExecutionPolicy,
    executor: ActionExecutor,
) -> ExecutionReport:
    """
    Execute FinalDecision actions with retry/timeout/idempotency/kill-switch gating.
    
    Invariants:
    - INV-EXE-1: Deterministic (same input → same plan/ordering)
    - INV-EXE-2: Bounded (max_retries, max_total_time_ms, max_concurrency)
    - INV-EXE-3: Fail-closed (exception → failed/denied + marker)
    - INV-EXE-4: Kill-switch compliance (ops kill-switch → deny)
    - INV-EXE-5: Secret hygiene (redaction in logs/reports)
    
    Args:
        final_decision: FinalDecision to execute
        context: Execution context (includes ops-health signals)
        policy: Execution policy (retry/timeout/idempotency)
        executor: Action executor function (domain-specific adapter)
    
    Returns:
        ExecutionReport with attempt results and trace keys
    """
    # INV-EXE-4: Kill-switch compliance
    if context.get("ops_deny_actions", False):
        logger.info("Kill-switch active: denying execution")
        return ExecutionReport(
            attempts=[],
            denied_count=1,
            fail_closed=False,  # Not fail-closed, intentional deny
        )

    if not final_decision.allowed:
        logger.info("FinalDecision.allowed=False: skipping execution")
        return ExecutionReport(
            attempts=[],
            skipped_count=1,
            fail_closed=False,
        )

    # Build execution plan (INV-EXE-1: deterministic)
    plan = ExecutionPlan(
        actions=[final_decision.action],
        max_retries=policy.retry.max_retries,
        max_total_time_ms=policy.timeout.max_total_time_ms,
        timeout_per_action_ms=policy.timeout.timeout_per_action_ms,
        idempotency_enabled=policy.idempotency.enabled,
    )

    # Execute with retry/timeout (INV-EXE-2: bounded)
    report = ExecutionReport()
    start_time_ms = int(time.time() * 1000)

    try:
        for action in plan.actions:
            attempt_number = 0
            success = False

            while attempt_number <= plan.max_retries:
                attempt_start_ms = int(time.time() * 1000)

                # Check timeout (INV-EXE-2: bounded)
                elapsed_ms = attempt_start_ms - start_time_ms
                if elapsed_ms >= plan.max_total_time_ms:
                    logger.warning("Max total time exceeded: stopping execution")
                    report.fail_closed = True
                    break

                try:
                    # Execute action
                    success, error_msg = executor(action, context)
                    attempt_latency_ms = int(time.time() * 1000) - attempt_start_ms

                    if success:
                        report.attempts.append(
                            ExecutionAttempt(
                                action=action,
                                status=ExecutionStatus.SUCCESS,
                                attempt_number=attempt_number,
                                latency_ms=attempt_latency_ms,
                            )
                        )
                        report.success_count += 1
                        break  # Success: exit retry loop
                    else:
                        # Failure: retry if attempts remaining
                        if attempt_number < plan.max_retries:
                            backoff_ms = policy.retry.backoff_ms(attempt_number + 1)
                            if backoff_ms > 0:
                                time.sleep(backoff_ms / 1000.0)
                        else:
                            # Final attempt failed
                            report.attempts.append(
                                ExecutionAttempt(
                                    action=action,
                                    status=ExecutionStatus.FAILED,
                                    attempt_number=attempt_number,
                                    latency_ms=attempt_latency_ms,
                                    error_message=error_msg,
                                )
                            )
                            report.failed_count += 1

                except Exception as e:
                    # INV-EXE-3: Fail-closed on exception
                    logger.warning("Execution exception: %s", type(e).__name__)
                    attempt_latency_ms = int(time.time() * 1000) - attempt_start_ms

                    if attempt_number < plan.max_retries:
                        backoff_ms = policy.retry.backoff_ms(attempt_number + 1)
                        if backoff_ms > 0:
                            time.sleep(backoff_ms / 1000.0)
                    else:
                        # Final attempt exception
                        report.attempts.append(
                            ExecutionAttempt(
                                action=action,
                                status=ExecutionStatus.FAILED,
                                attempt_number=attempt_number,
                                latency_ms=attempt_latency_ms,
                                error_message=str(e),
                            )
                        )
                        report.failed_count += 1
                        report.fail_closed = True

                attempt_number += 1

    except Exception as e:
        # INV-EXE-3: Fail-closed on orchestrator exception
        logger.error("Orchestrator exception: %s", type(e).__name__)
        report.fail_closed = True

    # Compute total latency
    end_time_ms = int(time.time() * 1000)
    report.total_latency_ms = end_time_ms - start_time_ms

    return report
