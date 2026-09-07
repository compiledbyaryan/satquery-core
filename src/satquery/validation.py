"""Pure guards and count arithmetic; no inference, raster IO, or metric-area promise."""
from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite

from .contracts import ArtifactRef, AssetRecord, GridSpec, InputSlot, ToolContract


def coordinate_cell_area(affine: tuple[float, float, float, float, float, float]) -> float:
    if not all(isfinite(x) for x in affine):
        raise ValueError("NONFINITE_GRID")
    a,b,_,d,e,_ = affine
    value=abs(a*e-b*d)
    if value == 0 or not isfinite(value):
        raise ValueError("INVALID_CELL_AREA")
    return value

def require_georeferencing(asset: AssetRecord) -> GridSpec:
    if asset.grid is None:
        raise ValueError("MISSING_GEOREFERENCE")
    return asset.grid

def validate_temporal_order(before: AssetRecord, after: AssetRecord) -> None:
    if before.acquired_at is None or after.acquired_at is None:
        raise ValueError("MISSING_TIME")
    if before.acquired_at >= after.acquired_at:
        raise ValueError("TEMPORAL_ORDER")

def validate_tool_inputs(contract: ToolContract,
                         inputs: Mapping[str, AssetRecord | ArtifactRef]) -> None:
    if set(inputs) != {slot.name for slot in contract.inputs}:
        raise ValueError("SLOTS")
    for slot in contract.inputs:
        item=inputs[slot.name]
        if not isinstance(slot,InputSlot):
            if not isinstance(item,ArtifactRef) or item.kind not in slot.accepted_kinds:
                raise ValueError("ARTIFACT_KIND")
            continue
        if not isinstance(item,AssetRecord):
            raise ValueError("ASSET_REQUIRED")
        asset=item
        if asset.modality not in slot.modalities:
            raise ValueError("MODALITY")
        if not set(slot.required_bands) <= set(asset.bands):
            raise ValueError("BANDS")
        if slot.requires_georeference:
            require_georeferencing(asset)

@dataclass(frozen=True)
class ChangeCounts:
    gained: int
    lost: int

    @property
    def net(self) -> int:
        return self.gained-self.lost

    @property
    def gross_turnover(self) -> int:
        return self.gained+self.lost

def change_counts(before: tuple[tuple[bool, ...], ...],
                  after: tuple[tuple[bool, ...], ...]) -> ChangeCounts:
    """Inputs cover the same valid domain; nodata must be removed upstream."""
    if not before or not before[0] or len(before) != len(after):
        raise ValueError("SHAPE")
    width=len(before[0])
    if any(len(row) != width for row in before+after):
        raise ValueError("SHAPE")
    if any(type(value) is not bool for row in before+after for value in row):
        raise ValueError("BINARY_REQUIRED")
    gained=lost=0
    for row0,row1 in zip(before,after,strict=True):
        for value0,value1 in zip(row0,row1,strict=True):
            gained += int(not value0 and value1)
            lost += int(value0 and not value1)
    return ChangeCounts(gained,lost)

def changed_descendants(parents: Mapping[str, tuple[str, ...]],
                        changed: tuple[str, ...]) -> tuple[str, ...]:
    """Include old changed versions and descendants, in deterministic topological order."""
    nodes=set(parents)
    if not set(changed) <= nodes:
        raise ValueError("UNKNOWN_CHANGED")
    if any(parent not in nodes for ps in parents.values() for parent in ps):
        raise ValueError("MISSING_PARENT")
    pending=set(nodes)
    ordered: list[str] = []
    while pending:
        ready=sorted(n for n in pending if not (set(parents[n]) & pending))
        if not ready:
            raise ValueError("CYCLE")
        ordered.extend(ready)
        pending.difference_update(ready)
    affected=set(changed)
    for node in ordered:
        if set(parents[node]) & affected:
            affected.add(node)
    return tuple(n for n in ordered if n in affected)
