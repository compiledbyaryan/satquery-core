"""Bi-temporal change detection and reasoning specialist adapter (Ticket T07)."""
import hashlib

from satquery.contracts import (
    ArtifactRef,
    AssetRecord,
    CheckResult,
    InputSlot,
    NamedOutput,
    TemporalParams,
    ToolContract,
    ToolResult,
)
from satquery.validation import validate_temporal_order


class TemporalSpecialist:
    """Scripted bi-temporal fixture behind a typed ToolContract (labelled mock).

    FIX-02: this adapter reads no pixels and loads no model. It is registered
    as implementation="mock" and refuses default execution with
    MODEL_UNAVAILABLE. Pass scripted=True only for explicitly labelled
    UI-fixture use; never in real analysis mode.
    """

    CONTRACT = ToolContract(
        tool_id="temporal_change",
        version="0.1.0",
        task="change_description",
        inputs=(
            InputSlot(
                name="before",
                modalities=("optical",),
                required_bands=("red", "green", "blue"),
            ),
            InputSlot(
                name="after",
                modalities=("optical",),
                required_bands=("red", "green", "blue"),
            ),
        ),
        output_kinds=("text", "mask"),
        params_kind="temporal",
        implementation="mock",
        timeout_seconds=60,
        max_memory_mb=2048,
    )

    def __init__(self, model_path: str | None = None, *, scripted: bool = False):
        self.model_path = model_path
        self.scripted = scripted

    def run(
        self,
        before: AssetRecord,
        after: AssetRecord,
        params: TemporalParams,
    ) -> ToolResult:
        before_time = before.acquired_at
        after_time = after.acquired_at
        if before_time is None or after_time is None:
            raise ValueError("MISSING_TIME")
        # Physical law: enforce strictly ordered timestamps (t0 < t1)
        validate_temporal_order(before, after)

        # Modality check: ensure both observations match contract
        if before.modality != "optical" or after.modality != "optical":
            raise ValueError("MODALITY_MISMATCH: Both observations must be optical.")

        if not self.scripted:
            raise ValueError(
                "MODEL_UNAVAILABLE: no real temporal provider configured; "
                "pass scripted=True only for labelled fixture use"
            )

        target = (params.target or "built_up").lower()
        days_apart = (after_time - before_time).days

        # Grounded change narrative
        description = (
            f"Bi-temporal evaluation ({before_time.date()} to {after_time.date()}, "
            f"{days_apart} days): Detectable expansion in {target} identified across northern sector."
        )

        desc_hash = hashlib.sha256(description.encode("utf-8")).hexdigest()
        mask_hash = hashlib.sha256(f"mask_{before.asset_id}_{after.asset_id}".encode()).hexdigest()

        return ToolResult(
            outputs=(
                NamedOutput(
                    name="change_summary",
                    artifact=ArtifactRef(
                        artifact_id=f"art_chg_{before.asset_id}_{after.asset_id}_summary",
                        sha256=desc_hash,
                        kind="text",
                    ),
                ),
                NamedOutput(
                    name="change_mask",
                    artifact=ArtifactRef(
                        artifact_id=f"art_chg_{before.asset_id}_{after.asset_id}_mask",
                        sha256=mask_hash,
                        kind="mask",
                    ),
                ),
            ),
            checks=(
                CheckResult(
                    check_id="temporal_order_check",
                    status="pass",
                    required=True,
                    detail=f"Validated temporal sequence: {before_time.isoformat()} < {after_time.isoformat()}",
                ),
            ),
            candidate_claims=(),
        )
