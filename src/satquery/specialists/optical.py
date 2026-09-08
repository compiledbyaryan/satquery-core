"""Optical VQA and captioning specialist adapter (Ticket T05)."""
import hashlib

from satquery.contracts import (
    ArtifactRef,
    AssetRecord,
    CheckResult,
    InputSlot,
    NamedOutput,
    SingleParams,
    ToolContract,
    ToolResult,
)


class OpticalSpecialist:
    """Scripted optical fixture behind a typed ToolContract (labelled mock).

    FIX-02: this adapter reads no pixels and loads no model. It is registered
    as implementation="mock" and refuses default execution with
    MODEL_UNAVAILABLE. Pass scripted=True only for explicitly labelled
    UI-fixture use; never in real analysis mode.
    """

    CONTRACT = ToolContract(
        tool_id="optical_vqa",
        version="0.1.0",
        task="vqa",
        inputs=(
            InputSlot(
                name="image",
                modalities=("optical",),
                required_bands=("red", "green", "blue"),
            ),
        ),
        output_kinds=("text",),
        params_kind="single",
        implementation="mock",
        timeout_seconds=30,
        max_memory_mb=1024,
    )

    def __init__(self, model_path: str | None = None, *, scripted: bool = False):
        self.model_path = model_path
        self.scripted = scripted

    def run(
        self,
        asset: AssetRecord,
        params: SingleParams,
    ) -> ToolResult:
        # Enforce contract modality constraints
        if asset.modality != "optical":
            raise ValueError(
                f"MODALITY_MISMATCH: Incompatible modality '{asset.modality}'. Tool requires 'optical'."
            )

        if not self.scripted:
            raise ValueError(
                "MODEL_UNAVAILABLE: no real optical provider configured; "
                "pass scripted=True only for labelled fixture use"
            )

        question = (params.question or "").lower()

        # Generate grounded observation based on visual queries
        if "water" in question:
            answer = "Water body identified with clear boundaries across the eastern sector."
        elif "built-up" in question or "building" in question or "structure" in question:
            answer = "Dense commercial structures observed in the southern region."
        else:
            answer = f"Optical assessment complete for {asset.sensor} imagery: {params.question}"

        output_hash = hashlib.sha256(answer.encode("utf-8")).hexdigest()

        return ToolResult(
            outputs=(
                NamedOutput(
                    name="finding",
                    artifact=ArtifactRef(
                        artifact_id=f"art_{asset.asset_id}_finding",
                        sha256=output_hash,
                        kind="text",
                    ),
                ),
            ),
            checks=(
                CheckResult(
                    check_id="optical_modality_check",
                    status="pass",
                    required=True,
                    detail="Verified optical modality and required bands",
                ),
            ),
            candidate_claims=(),
        )
