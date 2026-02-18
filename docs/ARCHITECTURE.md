<!--
Decision Ecosystem — execution-orchestration-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Architecture — execution-orchestration-core

## Overview

**execution-orchestration-core** provides domain-agnostic execution orchestration for `FinalDecision` actions. It ensures bounded, deterministic, fail-closed execution with kill-switch compliance and structured trace reporting.

---

## Core Components

### 1. Orchestrator (`orchestrator.py`)

**Main API:** `execute(FinalDecision, context, policy, executor) -> ExecutionReport`

- Coordinates retry/timeout/idempotency logic
- Enforces kill-switch compliance
- Handles exceptions (fail-closed)
- Produces execution report

### 2. Policies (`policies.py`)

**Types:**
- `RetryPolicy`: Exponential backoff, max retries
- `TimeoutPolicy`: Per-action and total timeouts
- `IdempotencyPolicy`: Idempotency key generation (policy only; see Idempotency status below)
- `ExecutionPolicy`: Complete policy bundle

**Invariant:** All policies are bounded (INV-EXE-2)

**Idempotency (current status):** Policy and model support `idempotency_enabled` and `key_generator` (e.g. `"action+context_hash"`). Key generation is **not yet implemented**: attempts are created with `idempotency_key=None`. When implementing, use `policy.idempotency.key_generator` to derive a key and set it on each `ExecutionAttempt` so that trace/verification data is complete.

### 3. Models (`model.py`)

**Types:**
- `ExecutionStatus`: success, failed, skipped, denied
- `ExecutionAttempt`: Single attempt result
- `ExecutionPlan`: Execution plan (deterministic)
- `ExecutionReport`: Final report with trace keys

### 4. Redaction (`redaction.py`)

**Function:** `redact_execution_log(log_data) -> redacted_dict`

- Redacts secret patterns from execution logs
- Case-insensitive pattern matching
- Nested dict/list support

**Invariant:** Secret hygiene (INV-EXE-5)

### 5. Trace (`trace.py`)

**Function:** `add_execution_trace(external, report) -> updated_external`

- Adds execution trace keys to `PacketV2.external`
- Keys follow INV-T1 format: `exec.*` namespace
- Format: `^[a-z0-9_]+(\.[a-z0-9_]+)+$`

---

## Design Principles

### Contract-First

- Depends only on `decision-schema`
- No cross-core dependencies
- Integration via shared types and context

### Domain Agnosticism

- No domain-specific vocabulary
- Generic action executor interface
- Domain adapters live in integration layer

### Fail-Closed Safety

- Exception → failed/denied + marker
- Kill-switch → deny execution
- Bounded execution (timeout/retry limits)

### Determinism

- Same input → same execution plan
- Deterministic retry ordering
- No randomness in core logic

---

## Execution Flow

```
FinalDecision + Context + Policy + Executor
    ↓
[Kill-switch check] → Deny if active
    ↓
[Allowed check] → Skip if not allowed
    ↓
[Build ExecutionPlan] (deterministic)
    ↓
[Execute with retry/timeout] (bounded)
    ↓
[Handle exceptions] (fail-closed)
    ↓
ExecutionReport → PacketV2.external trace keys
```

---

## Integration Points

### Input

- `FinalDecision`: From DMC (decision-modulation-core)
- `context`: Execution context (includes ops-health signals)
- `policy`: Execution policy (retry/timeout/idempotency)
- `executor`: Domain-specific action executor adapter

### Output

- `ExecutionReport`: Attempt results and metrics
- `PacketV2.external` trace keys: `exec.*` namespace

---

## Related Cores

- **decision-schema:** Contract types (FinalDecision, PacketV2)
- **decision-modulation-core:** Produces FinalDecision
- **ops-health-core:** Provides kill-switch signals
- **integration-harness:** Orchestrates full pipeline

---

**Last Updated:** 2026-02-17
