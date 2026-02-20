# Decision Ecosystem — execution-orchestration-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""Execution trace keys for PacketV2.external (INV-T1 compliant)."""

from typing import Any

from execution_orchestration_core.model import ExecutionReport


def add_execution_trace(external: dict[str, Any], report: ExecutionReport) -> dict[str, Any]:
    """
    Add execution trace keys to PacketV2.external dict.

    Keys follow INV-T1 format: exec.* namespace (dot-separated, lowercase).

    Args:
        external: Existing external dict
        report: Execution report

    Returns:
        Updated external dict with execution trace keys
    """
    updated = dict(external) if external else {}
    updated.update(report.to_external_dict())
    return updated
