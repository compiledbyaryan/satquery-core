"""Version 0.1 contracts. Structural validity never proves metadata or scene truth.

Use model_validate_json at wire boundaries. Store canonical immutable snapshots;
do not use model_construct or model_copy(update=...) to bypass validation.
"""
from datetime import datetime
from math import isfinite
from typing import Annotated, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
NonEmpty = Annotated[str, Field(min_length=1, max_length=1000, pattern=r"\S")]
Task = Literal["vqa", "caption", "grounding", "change_description", "change_vqa", "cross_modal",
               "inspect", "measure_change", "verify_claims"]
Modality = Literal["optical", "multispectral", "sar"]
ArtifactKind = Literal["text", "mask", "boxes", "metrics", "preview", "assertions", "report"]

class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, allow_inf_nan=False)
    schema_version: Literal["0.1"] = "0.1"

def aware(value: datetime | None) -> None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError("TIMEZONE_REQUIRED")

class GridSpec(Record):
    crs: NonEmpty
    # Rasterio/Affine convention: x=a*col+b*row+c; y=d*col+e*row+f.
    # This is NOT GDAL's (c,a,b,f,d,e) serialization order.
    affine: tuple[FiniteFloat, FiniteFloat, FiniteFloat, FiniteFloat, FiniteFloat, FiniteFloat]

    @model_validator(mode="after")
    def nonsingular(self) -> Self:
        a,b,_,d,e,_ = self.affine
        determinant = a*e-b*d
        if not isfinite(determinant) or determinant == 0:
            raise ValueError("SINGULAR_GRID")
        return self

class AssetRecord(Record):
    asset_id: Identifier
    version_id: Identifier
    sha256: Digest
    format: Literal["geotiff", "tiff", "png", "jpeg"]
    benchmark: Literal["VRSBench", "RSVQA", "CDVQA"] | None = None
    origin: Literal["public", "synthetic", "restricted"]
    modality: Modality
    sensor: NonEmpty
    processing_level: NonEmpty
    bands: tuple[NonEmpty, ...] = Field(min_length=1)
    width: Annotated[int, Field(gt=0, le=1000000)]
    height: Annotated[int, Field(gt=0, le=1000000)]
    units: NonEmpty = "unknown"
    acquired_at: datetime | None = None
    grid: GridSpec | None = None
    nodata_description: NonEmpty = "unknown"

    @model_validator(mode="after")
    def consistent(self) -> Self:
        aware(self.acquired_at)
        if len(set(self.bands)) != len(self.bands):
            raise ValueError("DUPLICATE_BANDS")
        if self.format in ("png","jpeg") and self.benchmark is None:
            raise ValueError("BENCHMARK_REQUIRED")
        return self

class ArtifactRef(Record):
    artifact_id: Identifier
    sha256: Digest
    kind: ArtifactKind

class InputSlot(Record):
    kind: Literal["asset"] = "asset"
    name: Identifier
    modalities: tuple[Modality, ...] = Field(min_length=1)
    required_bands: tuple[NonEmpty, ...] = ()
    requires_georeference: bool = False

class ArtifactSlot(Record):
    kind: Literal["artifact"] = "artifact"
    name: Identifier
    accepted_kinds: tuple[ArtifactKind, ...] = Field(min_length=1)

SlotSpec = Annotated[InputSlot | ArtifactSlot, Field(discriminator="kind")]

class ToolContract(Record):
    tool_id: Identifier
    version: NonEmpty
    task: Task
    inputs: tuple[SlotSpec, ...] = Field(min_length=1)
    output_kinds: tuple[ArtifactKind, ...] = Field(min_length=1)
    params_kind: Literal["single", "temporal", "fusion", "analysis"]
    implementation: Literal["real", "mock"]
    timeout_seconds: Annotated[int, Field(gt=0, le=3600)]
    max_memory_mb: Annotated[int, Field(gt=0)]
    allowed_targets: tuple[NonEmpty, ...] = ()

    @model_validator(mode="after")
    def unique_slots(self) -> Self:
        if len({i.name for i in self.inputs}) != len(self.inputs):
            raise ValueError("DUPLICATE_SLOT")
        expected = "analysis" if self.task in ("inspect","measure_change","verify_claims") else (
            "fusion" if self.task == "cross_modal" else (
            "temporal" if self.task.startswith("change_") else "single"))
        if self.params_kind != expected:
            raise ValueError("PARAM_KIND_TASK_MISMATCH")
        return self

class SingleParams(Record):
    kind: Literal["single"] = "single"
    task: Literal["vqa", "caption", "grounding"]
    question: NonEmpty | None = None
    target: NonEmpty | None = None

    @model_validator(mode="after")
    def required_fields(self) -> Self:
        if self.task == "vqa" and self.question is None:
            raise ValueError("QUESTION_REQUIRED")
        if self.task == "grounding" and self.target is None:
            raise ValueError("TARGET_REQUIRED")
        return self

class TemporalParams(Record):
    kind: Literal["temporal"] = "temporal"
    task: Literal["change_description", "change_vqa"]
    question: NonEmpty | None = None
    target: NonEmpty | None = None

    @model_validator(mode="after")
    def required_question(self) -> Self:
        if self.task == "change_vqa" and self.question is None:
            raise ValueError("QUESTION_REQUIRED")
        return self

class FusionParams(Record):
    kind: Literal["fusion"] = "fusion"
    task: Literal["cross_modal"] = "cross_modal"
    target: NonEmpty
    question: NonEmpty | None = None

class AnalysisParams(Record):
    kind: Literal["analysis"] = "analysis"
    task: Literal["inspect", "measure_change", "verify_claims"]
    unit: Literal["pixels", "m2", "ha"] = "pixels"

ToolParams = Annotated[SingleParams | TemporalParams | FusionParams | AnalysisParams, Field(discriminator="kind")]

class AssetInput(Record):
    kind: Literal["asset"] = "asset"
    slot: Identifier
    asset_version_id: Identifier

class OutputInput(Record):
    kind: Literal["output"] = "output"
    slot: Identifier
    producer_step: Identifier
    output_name: Identifier

InputBinding = Annotated[AssetInput | OutputInput, Field(discriminator="kind")]

class PlanStep(Record):
    step_id: Identifier
    tool_id: Identifier
    tool_version: NonEmpty
    depends_on: tuple[Identifier, ...] = ()
    inputs: tuple[InputBinding, ...] = Field(min_length=1)
    params: ToolParams

    @model_validator(mode="after")
    def unique_inputs(self) -> Self:
        if len({i.slot for i in self.inputs}) != len(self.inputs):
            raise ValueError("DUPLICATE_SLOT")
        if len(set(self.depends_on)) != len(self.depends_on):
            raise ValueError("DUPLICATE_DEPENDENCY")
        return self

class PlanRecord(Record):
    plan_id: Identifier
    task: Task
    asset_versions: tuple[Identifier, ...] = Field(min_length=1)
    steps: tuple[PlanStep, ...] = Field(min_length=1, max_length=20)
    max_repairs: Annotated[int, Field(ge=0, le=2)] = 1
    max_extra_checks: Annotated[int, Field(ge=0, le=3)] = 2

    @model_validator(mode="after")
    def ordered_dag(self) -> Self:
        if len(set(self.asset_versions)) != len(self.asset_versions):
            raise ValueError("DUPLICATE_ASSET_VERSION")
        seen: set[str] = set()
        for step in self.steps:
            if step.step_id in seen or not set(step.depends_on) <= seen:
                raise ValueError("INVALID_DEPENDENCY_ORDER")
            for binding in step.inputs:
                if isinstance(binding,AssetInput):
                    if binding.asset_version_id not in self.asset_versions:
                        raise ValueError("UNBOUND_ASSET")
                elif binding.producer_step not in step.depends_on:
                    raise ValueError("UNDECLARED_OUTPUT_DEPENDENCY")
            seen.add(step.step_id)
        if not any(step.params.task == self.task for step in self.steps):
            raise ValueError("REQUESTED_TASK_NOT_EXECUTED")
        return self

class ToolError(Record):
    code: Literal["INVALID_INPUT", "UNSUPPORTED", "TIMEOUT", "OUT_OF_MEMORY",
                  "MODEL_UNAVAILABLE", "INVALID_OUTPUT", "INTERNAL"]
    message: NonEmpty
    retryable: bool = False

class ExecutionEvent(Record):
    event_id: Identifier
    run_id: Identifier
    step_id: Identifier
    sequence: Annotated[int, Field(ge=1)]
    at: datetime
    status: Literal["started", "succeeded", "failed", "cancelled"]
    tool_id: Identifier
    tool_version: NonEmpty
    params: ToolParams
    inputs: tuple[Identifier, ...] = ()
    outputs: tuple[ArtifactRef, ...] = ()
    error: ToolError | None = None

    @model_validator(mode="after")
    def terminal_consistency(self) -> Self:
        aware(self.at)
        if self.status == "failed" and self.error is None:
            raise ValueError("ERROR_REQUIRED")
        if self.status != "failed" and self.error is not None:
            raise ValueError("UNEXPECTED_ERROR")
        if self.status == "succeeded" and not self.outputs:
            raise ValueError("OUTPUT_REQUIRED")
        if self.status != "succeeded" and self.outputs:
            raise ValueError("UNCOMMITTED_OUTPUT")
        return self

class CheckResult(Record):
    check_id: Identifier
    status: Literal["pass", "fail", "unknown", "not_applicable"]
    required: bool
    detail: NonEmpty

class CalibratedConfidence(Record):
    probability: Annotated[FiniteFloat, Field(ge=0, le=1)]
    calibration_id: Identifier
    population_scope: NonEmpty

class ClaimRecord(Record):
    claim_id: Identifier
    run_id: Identifier
    text: Annotated[str, Field(min_length=1, max_length=4000)]
    kind: Literal["observation", "measurement", "interpretation", "hypothesis"]
    status: Literal["supported", "partial", "unresolved", "stale"]
    evidence: tuple[ArtifactRef, ...]
    checks: tuple[CheckResult, ...]
    region_artifact: ArtifactRef | None = None
    confidence: CalibratedConfidence | None = None

    @model_validator(mode="after")
    def support_obligations(self) -> Self:
        if self.status == "supported":
            required = [c for c in self.checks if c.required]
            if not self.evidence or not required or any(c.status != "pass" for c in required):
                raise ValueError("SUPPORT_OBLIGATIONS_UNMET")
        return self

class ResolvedAsset(Record):
    kind: Literal["asset"] = "asset"
    slot: Identifier
    asset: AssetRecord

class ResolvedArtifact(Record):
    kind: Literal["artifact"] = "artifact"
    slot: Identifier
    artifact: ArtifactRef

ResolvedInput = Annotated[ResolvedAsset | ResolvedArtifact, Field(discriminator="kind")]

class NamedOutput(Record):
    name: Identifier
    artifact: ArtifactRef

class ToolContext(Record):
    run_id: Identifier
    step_id: Identifier
    inputs: tuple[ResolvedInput, ...] = Field(min_length=1)
    deadline: datetime

    @model_validator(mode="after")
    def time_valid(self) -> Self:
        aware(self.deadline)
        if len({i.slot for i in self.inputs}) != len(self.inputs):
            raise ValueError("DUPLICATE_SLOT")
        return self

class ToolResult(Record):
    outputs: tuple[NamedOutput, ...] = Field(min_length=1)
    checks: tuple[CheckResult, ...]
    candidate_claims: tuple[ClaimRecord, ...] = ()

    @model_validator(mode="after")
    def unique_names(self) -> Self:
        if len({o.name for o in self.outputs}) != len(self.outputs):
            raise ValueError("DUPLICATE_OUTPUT_NAME")
        return self

class Specialist(Protocol):
    @property
    def contract(self) -> ToolContract: ...

    async def execute(self, params: ToolParams, context: ToolContext) -> ToolResult: ...
