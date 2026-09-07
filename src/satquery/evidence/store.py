"""In-memory and persistent artifact store interface (Ticket T10)."""
from typing import Dict, Optional, Set
from satquery.contracts import ArtifactRef, AssetRecord, ClaimRecord


class ArtifactStore:
    """Manages asset references, generated artifacts, and atomic claims."""

    def __init__(self):
        self._assets: Dict[str, AssetRecord] = {}
        self._artifacts: Dict[str, ArtifactRef] = {}
        self._claims: Dict[str, ClaimRecord] = {}

    def register_asset(self, asset: AssetRecord) -> None:
        self._assets[asset.asset_id] = asset

    def get_asset(self, asset_id: str) -> Optional[AssetRecord]:
        return self._assets.get(asset_id)

    def store_artifact(self, artifact: ArtifactRef) -> None:
        self._artifacts[artifact.artifact_id] = artifact

    def get_artifact(self, artifact_id: str) -> Optional[ArtifactRef]:
        return self._artifacts.get(artifact_id)

    def has_artifact(self, artifact_id: str) -> bool:
        return artifact_id in self._artifacts

    def verify_claim_evidence(self, claim: ClaimRecord) -> bool:
        """Enforces that all evidence artifacts exist in the store."""
        for ev in claim.evidence:
            stored = self.get_artifact(ev.artifact_id)
            if not stored or stored.sha256 != ev.sha256:
                return False
        if claim.region_artifact:
            stored_region = self.get_artifact(claim.region_artifact.artifact_id)
            if not stored_region or stored_region.sha256 != claim.region_artifact.sha256:
                return False
        return True

    def record_claim(self, claim: ClaimRecord) -> None:
        if not self.verify_claim_evidence(claim):
            raise ValueError(f"CLAIM_UNSUPPORTED_BY_STORE: Claim '{claim.claim_id}' references unknown artifacts.")
        self._claims[claim.claim_id] = claim
