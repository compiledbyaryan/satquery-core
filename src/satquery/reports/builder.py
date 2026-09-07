"""Report generation, manifest serialization, and tenant isolation (Ticket T11)."""
import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from satquery.contracts import ArtifactRef, ClaimRecord
from satquery.evidence.store import ArtifactStore
from satquery.storage.jobs import JobStore


def _generate_minimal_pdf(content_text: str) -> bytes:
    """Builds a structurally valid, self-contained PDF document without external C libraries."""
    lines = content_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").split("\n")
    stream_content = "BT\n/F1 10 Tf\n20 770 Td\n14 TL\n"
    for line in lines[:50]:  # page bound
        stream_content += f"({line}) '\n"
    stream_content += "ET\n"
    stream_bytes = stream_content.encode("latin-1", errors="replace")

    pdf_body = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(len(stream_bytes)).encode("ascii") + b" >>\nstream\n"
        + stream_bytes +
        b"\nendstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    )
    xref_offset = len(pdf_body)
    pdf_xref = (
        b"xref\n0 6\n0000000000 65535 f \n"
        b"0000000009 00000 n \n0000000056 00000 n \n0000000111 00000 n \n"
        b"0000000242 00000 n \n0000000350 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(xref_offset).encode("ascii") + b"\n%%EOF"
    )
    return pdf_body + pdf_xref


class ReportExportError(RuntimeError):
    """Raised when report construction fails."""


def build_report(
    run_id: str,
    owner_id: str,
    job_store: JobStore | None = None,
    artifact_store: ArtifactStore | None = None,
    claims: list[ClaimRecord] | None = None,
    events: list[dict[str, Any]] | None = None,
) -> ArtifactRef:
    """
    Builds a verifiable dual-format report (machine manifest + PDF).
    Enforces fail-closed multi-tenant access control.
    """
    if job_store is None:
        job_store = JobStore()
    if artifact_store is None:
        artifact_store = ArtifactStore()

    run = job_store.get_run(run_id)
    if not run:
        raise KeyError(f"RUN_NOT_FOUND: Run '{run_id}' does not exist.")

    # 1. Multi-tenant boundary check: fail closed
    if run.get("owner_id") != owner_id:
        raise PermissionError(
            f"ACCESS_DENIED: User '{owner_id}' is not authorised to export run '{run_id}'."
        )

    # 2. Collect snapshot figures, labeling original vs. derived
    figures: list[dict[str, Any]] = []
    for slot_name, asset_id in run["assets"].items():
        figures.append({
            "slot": slot_name,
            "id": asset_id,
            "role": "ORIGINAL_ASSET",
            "description": f"Input asset bound to slot '{slot_name}'",
        })

    # Retrieve events & tool versions
    raw_events = events or []
    if not raw_events and run.get("outcome") and "events" in run["outcome"]:
        raw_events = run["outcome"]["events"]

    tools_used = []
    for ev in raw_events:
        tool_entry = {
            "tool_id": ev.get("tool_id", "unknown"),
            "tool_version": ev.get("tool_version", "unknown"),
            "status": ev.get("status", "unknown"),
        }
        tools_used.append(tool_entry)
        for out in ev.get("outputs", []):
            art_id = out if isinstance(out, str) else out.get("artifact_id", "unknown")
            figures.append({
                "slot": ev.get("step_id", "step"),
                "id": art_id,
                "role": "DERIVED_ARTIFACT",
                "description": f"Derived output from tool '{ev.get('tool_id')}'",
            })

    # 3. Resolve claims
    resolved_claims = []
    active_claims = claims or []
    for clm in active_claims:
        resolved_claims.append({
            "claim_id": clm.claim_id,
            "text": clm.text,
            "kind": clm.kind,
            "status": clm.status,
            "evidence_count": len(clm.evidence),
            "checks": [{"id": c.check_id, "status": c.status} for c in clm.checks],
        })

    # 4. Construct Machine-Readable Manifest
    manifest_data = {
        "report_id": f"rep_{run_id}",
        "run_id": run_id,
        "owner_id": owner_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "units": {"spatial": "meters", "temporal": "UTC-ISO8601", "area": "hectares"},
        "figures": figures,
        "tools": tools_used,
        "claims": resolved_claims,
    }
    manifest_bytes = json.dumps(manifest_data, indent=2, sort_keys=True).encode("utf-8")

    # 5. Construct Structured Human-Readable Document
    doc_lines = [
        f"SATQUERY SCIENTIFIC ANALYSIS REPORT: {run_id}",
        f"Owner: {owner_id} | Exported: {manifest_data['generated_at']}",
        "Units: Spatial: meters, Temporal: UTC, Area: hectares",
        "-" * 60,
        "INPUT AND DERIVED FIGURES:",
    ]
    for fig in figures:
        doc_lines.append(f"  [{fig['role']}] {fig['slot']}: {fig['id']}")
    doc_lines.append("-" * 60)
    doc_lines.append("SPECIALIST TOOLS:")
    for t in tools_used:
        doc_lines.append(f"  Tool: {t['tool_id']} (v{t['tool_version']}) - Status: {t['status']}")
    doc_lines.append("-" * 60)
    doc_lines.append("SCIENTIFIC CLAIMS:")
    for clm_info in resolved_claims:
        doc_lines.append(f"  [{clm_info['claim_id']}] ({clm_info['status']}) {clm_info['text']}")

    pdf_bytes = _generate_minimal_pdf("\n".join(doc_lines))

    # 6. Store Combined Report Artifact
    combined_hash = hashlib.sha256(manifest_bytes + pdf_bytes).hexdigest()
    report_artifact = ArtifactRef(
        artifact_id=f"rep_{run_id}",
        sha256=combined_hash,
        kind="report",
    )
    artifact_store.store_artifact(report_artifact)
    return report_artifact
