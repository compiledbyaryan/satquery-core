"""Deterministic plan controller and execution core (Ticket T10)."""
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel

from satquery.contracts import (
    ArtifactRef,
    AssetInput,
    ClaimRecord,
    ExecutionEvent,
    OutputInput,
    PlanRecord,
    ToolError,
    ToolResult,
)
from satquery.controller.registry import ToolRegistry
from satquery.evidence.store import ArtifactStore


class RunOutcome(BaseModel):
    """Aggregate result of an executed plan."""
    status: Literal["succeeded", "failed", "partial"]
    run_id: str
    events: tuple[ExecutionEvent, ...]
    artifacts: tuple[ArtifactRef, ...]
    claims: tuple[ClaimRecord, ...] = ()
    error: ToolError | None = None


def execute_plan(
    plan: PlanRecord,
    registry: ToolRegistry,
    store: ArtifactStore,
    mode: Literal["real", "mock"] = "real",
    simulate_timeout: bool = False,
) -> RunOutcome:
    run_id = f"run_{plan.plan_id}"
    events: list[ExecutionEvent] = []
    produced_artifacts: dict[str, ArtifactRef] = {}
    step_named_outputs: dict[str, dict[str, ArtifactRef]] = {}
    sequence = 1

    for step in plan.steps:
        # 1. Validate tool exists and matches execution bounds
        try:
            target = getattr(step.params, "target", None)
            contract, runner = registry.validate_executable(
                tool_id=step.tool_id,
                version=step.tool_version,
                target=target,
                mode=mode,
            )
        except ValueError as err:
            err_msg = str(err)
            err_code = "MOCK_PROHIBITED" if "MOCK_PROHIBITED" in err_msg else "UNSUPPORTED"
            tool_err = ToolError(code=err_code if err_code != "MOCK_PROHIBITED" else "UNSUPPORTED", message=err_msg)
            event = ExecutionEvent(
                event_id=f"evt_{step.step_id}_fail",
                run_id=run_id,
                step_id=step.step_id,
                sequence=sequence,
                at=datetime.now(UTC),
                status="failed",
                tool_id=step.tool_id,
                tool_version=step.tool_version,
                params=step.params,
                error=tool_err,
            )
            events.append(event)
            return RunOutcome(
                status="failed",
                run_id=run_id,
                events=tuple(events),
                artifacts=tuple(produced_artifacts.values()),
                error=tool_err,
            )

        # 2. Timeout handling: timeout never yields success
        if simulate_timeout:
            tool_err = ToolError(code="TIMEOUT", message=f"Tool exceeded timeout of {contract.timeout_seconds}s")
            event = ExecutionEvent(
                event_id=f"evt_{step.step_id}_timeout",
                run_id=run_id,
                step_id=step.step_id,
                sequence=sequence,
                at=datetime.now(UTC),
                status="failed",
                tool_id=step.tool_id,
                tool_version=step.tool_version,
                params=step.params,
                error=tool_err,
            )
            events.append(event)
            return RunOutcome(
                status="failed",
                run_id=run_id,
                events=tuple(events),
                artifacts=tuple(produced_artifacts.values()),
                error=tool_err,
            )

        # 3. Resolve input bindings
        call_kwargs = {"params": step.params}
        bound_inputs: list[str] = []

        for binding in step.inputs:
            if isinstance(binding, AssetInput):
                asset = store.get_asset(binding.asset_version_id)
                if not asset:
                    tool_err = ToolError(code="INVALID_INPUT", message=f"Asset '{binding.asset_version_id}' missing")
                    event = ExecutionEvent(
                        event_id=f"evt_{step.step_id}_err",
                        run_id=run_id,
                        step_id=step.step_id,
                        sequence=sequence,
                        at=datetime.now(UTC),
                        status="failed",
                        tool_id=step.tool_id,
                        tool_version=step.tool_version,
                        params=step.params,
                        error=tool_err,
                    )
                    events.append(event)
                    return RunOutcome(status="failed", run_id=run_id, events=tuple(events), artifacts=tuple(produced_artifacts.values()), error=tool_err)
                call_kwargs[binding.slot] = asset
                bound_inputs.append(binding.asset_version_id)
            elif isinstance(binding, OutputInput):
                producer_outputs = step_named_outputs.get(binding.producer_step, {})
                artifact = producer_outputs.get(binding.output_name)
                if not artifact:
                    tool_err = ToolError(code="INVALID_INPUT", message=f"Output '{binding.output_name}' from '{binding.producer_step}' missing")
                    event = ExecutionEvent(
                        event_id=f"evt_{step.step_id}_err",
                        run_id=run_id,
                        step_id=step.step_id,
                        sequence=sequence,
                        at=datetime.now(UTC),
                        status="failed",
                        tool_id=step.tool_id,
                        tool_version=step.tool_version,
                        params=step.params,
                        error=tool_err,
                    )
                    events.append(event)
                    return RunOutcome(status="failed", run_id=run_id, events=tuple(events), artifacts=tuple(produced_artifacts.values()), error=tool_err)
                call_kwargs[binding.slot] = artifact
                bound_inputs.append(artifact.artifact_id)

        # 4. Invoke runner
        try:
            if hasattr(runner, "run"):
                result: ToolResult = runner.run(**call_kwargs)
            else:
                result = runner(**call_kwargs)
        except Exception as err:  # noqa: BLE001 -- runner boundary normalizes provider failures
            tool_err = ToolError(code="INTERNAL", message=str(err))
            event = ExecutionEvent(
                event_id=f"evt_{step.step_id}_err",
                run_id=run_id,
                step_id=step.step_id,
                sequence=sequence,
                at=datetime.now(UTC),
                status="failed",
                tool_id=step.tool_id,
                tool_version=step.tool_version,
                params=step.params,
                error=tool_err,
            )
            events.append(event)
            return RunOutcome(status="failed", run_id=run_id, events=tuple(events), artifacts=tuple(produced_artifacts.values()), error=tool_err)

        # 5. Fail-Closed Verification: required checks must pass
        for chk in result.checks:
            if chk.required and chk.status != "pass":
                tool_err = ToolError(code="INVALID_OUTPUT", message=f"Required check failed: {chk.detail}")
                event = ExecutionEvent(
                    event_id=f"evt_{step.step_id}_check_fail",
                    run_id=run_id,
                    step_id=step.step_id,
                    sequence=sequence,
                    at=datetime.now(UTC),
                    status="failed",
                    tool_id=step.tool_id,
                    tool_version=step.tool_version,
                    params=step.params,
                    error=tool_err,
                )
                events.append(event)
                return RunOutcome(status="failed", run_id=run_id, events=tuple(events), artifacts=tuple(produced_artifacts.values()), error=tool_err)

        # 6. Record step outputs into the store
        step_named_outputs[step.step_id] = {}
        step_outputs: list[ArtifactRef] = []
        for out in result.outputs:
            store.store_artifact(out.artifact)
            produced_artifacts[out.artifact.artifact_id] = out.artifact
            step_named_outputs[step.step_id][out.name] = out.artifact
            step_outputs.append(out.artifact)

        event = ExecutionEvent(
            event_id=f"evt_{step.step_id}_succ",
            run_id=run_id,
            step_id=step.step_id,
            sequence=sequence,
            at=datetime.now(UTC),
            status="succeeded",
            tool_id=step.tool_id,
            tool_version=step.tool_version,
            params=step.params,
            inputs=tuple(bound_inputs),
            outputs=tuple(step_outputs),
        )
        events.append(event)
        sequence += 1

    return RunOutcome(
        status="succeeded",
        run_id=run_id,
        events=tuple(events),
        artifacts=tuple(produced_artifacts.values()),
    )
