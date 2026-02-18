# Threat Model — execution-orchestration-core

## Security Assumptions

### Trust Boundaries

- **Trusted:** `FinalDecision` from DMC, `context` from integration layer
- **Untrusted:** Action executor adapter (domain-specific, may be external)
- **Trusted:** `ExecutionPolicy` (from integration layer)

### Attack Surfaces

1. **Action Executor:** Domain-specific adapter may be malicious or buggy
2. **Execution Context:** May contain sensitive data (requires redaction)
3. **Execution Logs:** May leak secrets (requires redaction)

---

## Mitigations

### INV-EXE-3: Fail-Closed Safety

- **Threat:** Executor exception causes unsafe execution
- **Mitigation:** Exception → failed/denied + marker, no unsafe execution

### INV-EXE-4: Kill-Switch Compliance

- **Threat:** Execution proceeds despite kill-switch
- **Mitigation:** Check `ops_deny_actions` before execution, deny if active

### INV-EXE-5: Secret Hygiene

- **Threat:** Secrets leaked in execution logs/reports
- **Mitigation:** Redact secret patterns before logging/reporting

### INV-EXE-2: Boundedness

- **Threat:** Unbounded retries/timeouts cause DoS
- **Mitigation:** Enforce `max_retries`, `max_total_time_ms`, `max_concurrency`

---

## Security Invariants

- **INV-EXE-3:** Exception → fail-closed (no unsafe execution)
- **INV-EXE-4:** Kill-switch → deny (no execution when unsafe)
- **INV-EXE-5:** Secrets redacted (no leakage)
- **INV-EXE-2:** Execution bounded (no DoS)

---

**Last Updated:** 2026-02-17
