<!--
Decision Ecosystem — execution-orchestration-core
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Parameter Index — Execution Context Keys

**Purpose:** Document execution context keys used by execution-orchestration-core  
**Note:** This is core-level documentation; SSOT is `decision-schema/docs/PARAMETER_INDEX.md`

---

## Execution Context Keys

### Kill-Switch Keys

| Key | Type | Description | Source |
|-----|------|-------------|--------|
| `ops_deny_actions` | `bool` | Kill-switch active flag | ops-health-core |

**Usage:** If `ops_deny_actions=True`, execution is denied (INV-EXE-4).

---

### Timing Keys

| Key | Type | Description | Source |
|-----|------|-------------|--------|
| `now_ms` | `int` | Current time (milliseconds) | Integration layer |

**Usage:** Used for timeout calculations and idempotency key generation.

---

## PacketV2.external Trace Keys (exec.* namespace)

Execution report adds these keys to `PacketV2.external`:

| Key | Type | Description |
|-----|------|-------------|
| `exec.total_latency_ms` | `int` | Total execution latency |
| `exec.success_count` | `int` | Number of successful attempts |
| `exec.failed_count` | `int` | Number of failed attempts |
| `exec.skipped_count` | `int` | Number of skipped actions |
| `exec.denied_count` | `int` | Number of denied actions |
| `exec.fail_closed` | `bool` | Fail-closed marker |
| `exec.attempt_count` | `int` | Total attempt count |

**Format:** All keys follow INV-T1 format: `^[a-z0-9_]+(\.[a-z0-9_]+)+$`

**Registration:** Keys should be registered in `decision-schema/trace_registry.py` (future).

---

## Related Documentation

- **decision-schema/docs/PARAMETER_INDEX.md:** SSOT for context keys
- **decision-schema/docs/TRACE_KEY_REGISTRY.md:** Trace key registry

---

**Last Updated:** 2026-02-17
