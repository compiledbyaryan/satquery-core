"""Optical-SAR cross-modal fusion specialist adapter (Ticket T08)."""
import hashlib

from satquery.contracts import (
    ArtifactRef,
    AssetRecord,
    CheckResult,
    FusionParams,
    InputSlot,
    NamedOutput,
    ToolContract,
    ToolResult,
)


class FusionSpecialist:
    """Scripted optical-SAR fixture behind a typed ToolContract (labelled mock).

    FIX-02: this adapter reads no pixels and loads no model. It is registered
    as implementation="mock" and refuses default execution with
    MODEL_UNAVAILABLE. Pass scripted=True only for explicitly labelled
    UI-fixture use; never in real analysis mode.
    """

    CONTRACT = ToolContract(
        tool_id="optical_sar_fusion",
        version="0.1.0",
        task="cross_modal",
        inputs=(
            InputSlot(
                name="optical",
                modalities=("optical",),
                required_bands=("red", "green", "blue"),
            ),
            InputSlot(
                name="sar",
                modalities=("sar",),
                required_bands=("vv", "vh"),
            ),
        ),
        output_kinds=("text", "metrics"),
        params_kind="fusion",
        implementation="mock",
        timeout_seconds=60,
        max_memory_mb=2048,
    )

    def __init__(self, model_path: str | None = None, *, scripted: bool = False):
        self.model_path = model_path
        self.scripted = scripted

    def run(
        self,
        optical: AssetRecord,
        sar: AssetRecord,
        params: FusionParams,
    ) -> ToolResult:
        # Enforce modality constraints for both slots
        if optical.modality != "optical":
            raise ValueError(
                f"MODALITY_MISMATCH: 'optical' slot requires optical imagery, got '{optical.modality}'."
            )
        if sar.modality != "sar":
            raise ValueError(
                f"MODALITY_MISMATCH: 'sar' slot requires SAR imagery, got '{sar.modality}'."
            )

        if not self.scripted:
            raise ValueError(
                "MODEL_UNAVAILABLE: no real fusion provider configured; "
                "pass scripted=True only for labelled fixture use"
            )

        target = params.target.lower()

        # Joint inference combining multi-spectral color and microwave backscatter
        summary = (
            f"Cross-modal analysis for {target}: Optical ({optical.sensor}) spectral response "
            f"corroborated by SAR ({sar.sensor}) backscatter returns across shared domain."
        )

        metrics_payload = f"optical_entropy:0.82;sar_backscatter_mean:-12.4dB;target:{target}"

        summary_hash = hashlib.sha256(summary.encode("utf-8")).hexdigest()
        metrics_hash = hashlib.sha256(metrics_payload.encode("utf-8")).hexdigest()

        return ToolResult(
            outputs=(
                NamedOutput(
                    name="fusion_summary",
                    artifact=ArtifactRef(
                        artifact_id=f"art_fus_{optical.asset_id}_{sar.asset_id}_summary",
                        sha256=summary_hash,
                        kind="text",
                    ),
                ),
                NamedOutput(
                    name="fusion_metrics",
                    artifact=ArtifactRef(
                        artifact_id=f"art_fus_{optical.asset_id}_{sar.asset_id}_metrics",
                        sha256=metrics_hash,
                        kind="metrics",
                    ),
                ),
            ),
            checks=(
                CheckResult(
                    check_id="cross_modal_alignment_check",
                    status="pass",
                    required=True,
                    detail=f"Correlated optical ({optical.asset_id}) with SAR ({sar.asset_id})",
                ),
            ),
            candidate_claims=(),
        )
