"""Behavior tests runnable with unittest or pytest; no satellite downloads needed."""
import json
import unittest
from datetime import UTC, datetime

from pydantic import ValidationError

from satquery.contracts import (
    ArtifactRef,
    ArtifactSlot,
    AssetInput,
    AssetRecord,
    CheckResult,
    ClaimRecord,
    ExecutionEvent,
    GridSpec,
    InputSlot,
    NamedOutput,
    OutputInput,
    PlanRecord,
    PlanStep,
    ResolvedArtifact,
    ResolvedAsset,
    SingleParams,
    ToolContext,
    ToolContract,
    ToolResult,
)
from satquery.validation import (
    change_counts,
    changed_descendants,
    coordinate_cell_area,
    require_georeferencing,
    validate_temporal_order,
    validate_tool_inputs,
)

NOW = datetime(2026, 1, 1, tzinfo=UTC)

def asset(**overrides):
    data = dict(asset_id="asset_a", version_id="version_a", sha256="a" * 64,
                format="geotiff", modality="optical", sensor="synthetic",
                bands=("red", "green", "blue"), width=2, height=2,
                acquired_at=NOW, origin="synthetic", processing_level="fixture",
                grid=GridSpec(crs="EPSG:32643", affine=(10.,0.,0.,0.,-10.,0.)))
    data.update(overrides)
    return AssetRecord(**data)

def contract():
    return ToolContract(tool_id="optical_vqa", version="0.1.0", task="vqa",
        inputs=(InputSlot(name="image", modalities=("optical",),
                          required_bands=("red","green","blue")),),
        output_kinds=("text",), params_kind="single", implementation="real",
        timeout_seconds=30, max_memory_mb=1024)

class ContractTests(unittest.TestCase):
    def test_overflowing_determinant_rejected(self):
        with self.assertRaises(ValidationError):
            GridSpec(crs="EPSG:4326",affine=(1e308,1e308,0.,1e308,1e308,0.))

    def test_blank_question_rejected(self):
        with self.assertRaises(ValidationError): SingleParams(task="vqa",question="   ")

    def test_context_preserves_temporal_slots(self):
        context=ToolContext(run_id="r",step_id="s",deadline=NOW,inputs=(
            ResolvedAsset(slot="before",asset=asset()),
            ResolvedAsset(slot="after",asset=asset(version_id="version_b"))))
        restored=ToolContext.model_validate_json(context.model_dump_json())
        self.assertEqual([i.slot for i in restored.inputs],["before","after"])

    def test_named_masks_can_be_resolved_distinctly(self):
        before=ArtifactRef(artifact_id="mask_before",sha256="a"*64,kind="mask")
        after=ArtifactRef(artifact_id="mask_after",sha256="b"*64,kind="mask")
        result=ToolResult(outputs=(NamedOutput(name="before_mask",artifact=before),
            NamedOutput(name="after_mask",artifact=after)),checks=())
        resolved=next(o.artifact for o in result.outputs if o.name=="after_mask")
        context=ToolContext(run_id="r",step_id="s",deadline=NOW,
            inputs=(ResolvedArtifact(slot="mask",artifact=resolved),))
        self.assertEqual(context.inputs[0].artifact.artifact_id,"mask_after")

    def test_duplicate_output_names_rejected(self):
        output=NamedOutput(name="mask",artifact=ArtifactRef(artifact_id="a",sha256="a"*64,kind="mask"))
        with self.assertRaises(ValidationError): ToolResult(outputs=(output,output),checks=())

    def test_artifact_slot_validates_kind(self):
        tool=ToolContract(tool_id="mask_caption",version="1",task="caption",
            inputs=(ArtifactSlot(name="mask",accepted_kinds=("mask",)),),
            output_kinds=("text",),params_kind="single",implementation="real",
            timeout_seconds=10,max_memory_mb=100)
        validate_tool_inputs(tool,{"mask":ArtifactRef(artifact_id="a",sha256="a"*64,kind="mask")})
        with self.assertRaisesRegex(ValueError,"ARTIFACT_KIND"):
            validate_tool_inputs(tool,{"mask":ArtifactRef(artifact_id="a",sha256="a"*64,kind="text")})

    def test_asset_json_round_trip(self):
        item=asset()
        self.assertEqual(AssetRecord.model_validate_json(item.model_dump_json()),item)

    def test_unknown_fields_rejected(self):
        with self.assertRaises(ValidationError): asset(surprise=True)

    def test_numeric_string_dimensions_rejected(self):
        with self.assertRaises(ValidationError): asset(width="2")

    def test_duplicate_bands_rejected(self):
        with self.assertRaises(ValidationError): asset(bands=("red","red"))

    def test_nan_affine_rejected(self):
        with self.assertRaises(ValidationError):
            GridSpec(crs="EPSG:4326",affine=(float("nan"),0.,0.,0.,1.,0.))

    def test_singular_affine_rejected(self):
        with self.assertRaises(ValidationError):
            GridSpec(crs="EPSG:4326",affine=(1.,2.,0.,2.,4.,0.))

    def test_naive_acquisition_time_rejected(self):
        with self.assertRaises(ValidationError): asset(acquired_at=datetime(2026,1,1))

    def test_png_requires_benchmark_identity(self):
        with self.assertRaises(ValidationError): asset(format="png")

    def test_benchmark_png_allowed(self):
        self.assertEqual(asset(format="png",benchmark="VRSBench").format,"png")

    def test_missing_crs_blocks_geospatial_operation(self):
        with self.assertRaisesRegex(ValueError,"MISSING_GEOREFERENCE"):
            require_georeferencing(asset(grid=None))

    def test_missing_crs_does_not_block_ingestion_record(self):
        self.assertIsNone(asset(grid=None).grid)

    def test_reverse_dates_rejected(self):
        earlier=asset(version_id="version_b",acquired_at=NOW.replace(year=2025))
        with self.assertRaisesRegex(ValueError,"TEMPORAL_ORDER"):
            validate_temporal_order(asset(),earlier)

    def test_equal_dates_rejected_for_real_change(self):
        with self.assertRaisesRegex(ValueError,"TEMPORAL_ORDER"):
            validate_temporal_order(asset(),asset(version_id="version_b"))

    def test_missing_time_rejected_for_change(self):
        with self.assertRaisesRegex(ValueError,"MISSING_TIME"):
            validate_temporal_order(asset(acquired_at=None),asset())

    def test_correct_dates_accepted(self):
        validate_temporal_order(asset(),asset(version_id="version_b",
                               acquired_at=NOW.replace(year=2027)))

    def test_sar_cannot_enter_optical_tool(self):
        with self.assertRaisesRegex(ValueError,"MODALITY"):
            validate_tool_inputs(contract(),{"image":asset(modality="sar",bands=("VV",))})

    def test_missing_band_rejected(self):
        with self.assertRaisesRegex(ValueError,"BANDS"):
            validate_tool_inputs(contract(),{"image":asset(bands=("red",))})

    def test_valid_tool_inputs_accepted(self):
        validate_tool_inputs(contract(),{"image":asset()})

    def test_unexpected_slot_rejected(self):
        with self.assertRaisesRegex(ValueError,"SLOTS"):
            validate_tool_inputs(contract(),{"other":asset()})

    def test_claim_cannot_be_supported_without_evidence(self):
        with self.assertRaises(ValidationError):
            ClaimRecord(claim_id="c",run_id="r",text="Water is present",kind="interpretation",
                status="supported",evidence=(),checks=())

    def test_failing_required_check_blocks_supported_claim(self):
        with self.assertRaises(ValidationError):
            ClaimRecord(claim_id="c",run_id="r",text="Water is present",kind="interpretation",
                status="supported",evidence=(ArtifactRef(artifact_id="x",sha256="a"*64,kind="mask"),),
                checks=(CheckResult(check_id="q",status="fail",required=True,detail="bad"),))

    def test_unresolved_claim_is_representable(self):
        c=ClaimRecord(claim_id="c",run_id="r",text="Water presence is unresolved",
                      kind="interpretation",status="unresolved",evidence=(),checks=())
        self.assertEqual(c.status,"unresolved")

    def test_failed_event_needs_error(self):
        with self.assertRaises(ValidationError):
            ExecutionEvent(event_id="e",run_id="r",step_id="s",sequence=1,
                           at=NOW,status="failed",tool_id="t",tool_version="1",
                           params=SingleParams(task="vqa",question="What is visible?"))

    def test_plan_rejects_unknown_dependency(self):
        with self.assertRaises(ValidationError):
            PlanRecord(plan_id="p",task="vqa",asset_versions=("version_a",),
                steps=(PlanStep(step_id="s",tool_id="t",tool_version="1",depends_on=("missing",),
                    inputs=(AssetInput(slot="image",asset_version_id="version_a"),),
                    params=SingleParams(task="vqa",question="What?")),))

    def test_plan_rejects_unbound_asset(self):
        with self.assertRaises(ValidationError):
            PlanRecord(plan_id="p",task="vqa",asset_versions=("other",),
                steps=(PlanStep(step_id="s",tool_id="t",tool_version="1",
                    inputs=(AssetInput(slot="image",asset_version_id="version_a"),),
                    params=SingleParams(task="vqa",question="What?")),))

    def test_output_reference_requires_declared_dependency(self):
        with self.assertRaises(ValidationError):
            PlanRecord(plan_id="p",task="caption",asset_versions=("version_a",),steps=(
                PlanStep(step_id="a",tool_id="t",tool_version="1",
                    inputs=(AssetInput(slot="image",asset_version_id="version_a"),),
                    params=SingleParams(task="caption")),
                PlanStep(step_id="b",tool_id="t",tool_version="1",
                    inputs=(OutputInput(slot="image",producer_step="a",output_name="mask"),),
                    params=SingleParams(task="caption"))))

    def test_schema_generation_for_all_core_records(self):
        for cls in (AssetRecord,ToolContract,PlanRecord,ExecutionEvent,ClaimRecord):
            with self.subTest(record=cls.__name__):
                self.assertEqual(cls.model_json_schema()["additionalProperties"],False)
                json.dumps(cls.model_json_schema(),allow_nan=False)

class MathematicsAndGraphTests(unittest.TestCase):
    def test_affine_determinant_includes_rotation_terms(self):
        self.assertEqual(coordinate_cell_area((3.,2.,0.,1.,4.,0.)),10.)

    def test_gains_are_not_net_change(self):
        r=change_counts(((True,False),(False,False)),((False,True),(True,False)))
        self.assertEqual((r.gained,r.lost,r.net,r.gross_turnover),(2,1,1,3))

    def test_temporal_reversal_reverses_net(self):
        a=((True,False),);b=((False,False),)
        self.assertEqual(change_counts(a,b).net,-change_counts(b,a).net)

    def test_shape_mismatch_rejected(self):
        with self.assertRaises(ValueError): change_counts(((True,),),((True,False),))

    def test_non_binary_input_rejected(self):
        with self.assertRaises(ValueError): change_counts(((2,),),((True,),))

    def test_selective_invalidation_uses_old_version_dependencies(self):
        graph={"old_image":(),"other_image":(),"mask":("old_image",),
               "area":("mask",),"claim":("area",),"other_claim":("other_image",)}
        self.assertEqual(changed_descendants(graph,("old_image",)),
                         ("old_image","mask","area","claim"))

    def test_cycle_rejected(self):
        with self.assertRaisesRegex(ValueError,"CYCLE"):
            changed_descendants({"a":("b",),"b":("a",)},("a",))

    def test_missing_graph_parent_rejected(self):
        with self.assertRaisesRegex(ValueError,"MISSING_PARENT"):
            changed_descendants({"a":("b",)},("a",))

    def test_unknown_changed_node_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_CHANGED"):
            changed_descendants({"old":()},("new",))

if __name__ == "__main__": unittest.main()
