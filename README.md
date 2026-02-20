<!--
Decision Ecosystem — execution-orchestration-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# execution-orchestration-core

**Domain-agnostic execution orchestration core for FinalDecision actions: retries, timeouts, idempotency, kill-switch gating, and PacketV2 execution trace/reporting.**

---

## Purpose

**execution-orchestration-core** is a domain-agnostic runtime component that executes `FinalDecision.actions` safely and deterministically. It provides bounded retries/backoff, timeouts, idempotency keys, kill-switch gating (via ops signals), and produces a structured execution report suitable for `PacketV2` trace/audit pipelines. This core depends only on `decision-schema` and intentionally excludes any vendor- or domain-specific adapters.

---

## Responsibilities

- **Action execution orchestration:** Execute `FinalDecision.actions` with retry/timeout/idempotency
- **Kill-switch compliance:** Respect ops-health kill-switch signals (deny execution when active)
- **Fail-closed safety:** Exception handling with safe defaults and markers
- **Execution trace:** Produce `PacketV2.external` trace keys (INV-T1 compliant)
- **Secret hygiene:** Redact sensitive data in execution logs/reports

---

## Contracts

- **Input:** `FinalDecision`, execution context, `ExecutionPolicy`, action executor adapter
- **Output:** `ExecutionReport` with attempt results and trace keys
- **Dependency:** Only `decision-schema` (contract-first)

---

## Integration

**Core API:** `execute(FinalDecision, context, policy, executor) -> ExecutionReport`

```python
from decision_schema.types import Action, FinalDecision
from execution_orchestration_core.orchestrator import execute
from execution_orchestration_core.policies import ExecutionPolicy

# FinalDecision from DMC
final_decision = FinalDecision(action=Action.ACT, allowed=True, reasons=["signal_detected"])

# Execution context (includes ops-health signals)
context = {
    "now_ms": 1000,
    "ops_deny_actions": False,  # Kill-switch check
}

# Execution policy
policy = ExecutionPolicy()

# Domain-specific executor adapter
def my_executor(action: Action, ctx: dict) -> tuple[bool, str | None]:
    # Domain-specific execution logic
    if action == Action.ACT:
        # Execute action...
        return True, None
    return False, "unsupported action"

# Execute
report = execute(final_decision, context, policy, my_executor)

# Attach to PacketV2.external
from execution_orchestration_core.trace import add_execution_trace
packet.external = add_execution_trace(packet.external or {}, report)
```

---

## Invariants

- **INV-EXE-1:** Deterministic execution (same input → same plan/ordering)
- **INV-EXE-2:** Bounded execution (max_retries, max_total_time_ms, max_concurrency)
- **INV-EXE-3:** Fail-closed on exception (unsafe execution prevented)
- **INV-EXE-4:** Kill-switch compliance (ops kill-switch → deny)
- **INV-EXE-5:** Secret hygiene (redaction in logs/reports)
- **INV-EXE-6:** Rate-limit safety (per-action and global limits)

---

## Installation

```bash
pip install -e .
```

Or from git:
```bash
pip install git+https://github.com/MchtMzffr/execution-orchestration-core.git
```

---

## Tests

```bash
pytest tests/
```

---

## Documentation

- `docs/ARCHITECTURE.md`: System architecture
- `docs/PARAMETER_INDEX_EXECUTION.md`: Execution context keys
- `docs/THREAT_MODEL.md`: Security and threat model

---

## License

MIT License. See [LICENSE](LICENSE).
