# Release Notes — execution-orchestration-core 0.1.0

**Release Date:** 2026-02-17  
**Type:** Initial Release

---

## Summary

Initial release of execution-orchestration-core: domain-agnostic execution orchestration for FinalDecision actions with retry/timeout/idempotency/kill-switch gating and PacketV2 trace reporting.

---

## Features

### Core Functionality

- **Execution Orchestration:** Execute `FinalDecision.actions` with retry/timeout/idempotency
- **Kill-Switch Compliance:** Respect ops-health kill-switch signals
- **Fail-Closed Safety:** Exception handling with safe defaults
- **Execution Trace:** Produce `PacketV2.external` trace keys (INV-T1 compliant)
- **Secret Hygiene:** Redact sensitive data in execution logs

### Invariants

- **INV-EXE-1:** Deterministic execution
- **INV-EXE-2:** Bounded execution (max_retries, max_total_time_ms)
- **INV-EXE-3:** Fail-closed on exception
- **INV-EXE-4:** Kill-switch compliance
- **INV-EXE-5:** Secret hygiene
- **INV-EXE-6:** Rate-limit safety (future)

---

## API

**Main API:** `execute(FinalDecision, context, policy, executor) -> ExecutionReport`

**Dependencies:** Only `decision-schema>=0.2,<0.3`

---

## Testing

- ✅ All invariant tests pass
- ✅ Fail-closed behavior verified
- ✅ Kill-switch compliance verified
- ✅ Secret hygiene verified

---

## Upgrade Path

```bash
pip install "execution-orchestration-core>=0.1.0,<0.2"
```

---

**Last Updated:** 2026-02-17
