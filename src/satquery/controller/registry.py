"""Tool registry and contract boundary enforcement (Ticket T10)."""
from typing import Any

from satquery.contracts import ToolContract


class ToolRegistry:
    """Stores validated ToolContracts and their executable runners."""

    def __init__(self) -> None:
        self._tools: dict[tuple[str, str], tuple[ToolContract, Any]] = {}

    def register(self, contract: ToolContract, runner: Any) -> None:
        self._tools[(contract.tool_id, contract.version)] = (contract, runner)

    def get(self, tool_id: str, version: str) -> tuple[ToolContract, Any] | None:
        return self._tools.get((tool_id, version))

    def validate_executable(
        self,
        tool_id: str,
        version: str,
        target: str | None = None,
        mode: str = "real",
    ) -> tuple[ToolContract, Any]:
        entry = self.get(tool_id, version)
        if entry is None:
            raise ValueError(f"UNREGISTERED_TOOL: Tool '{tool_id}' version '{version}' not found in registry.")

        contract, runner = entry

        # Mode safety check: mock tools are prohibited when executing in real mode
        if mode == "real" and contract.implementation == "mock":
            raise ValueError(f"MOCK_PROHIBITED: Tool '{tool_id}' is a mock implementation but mode is 'real'.")

        # Target verification
        if target and contract.allowed_targets and target not in contract.allowed_targets:
            raise ValueError(
                f"UNSUPPORTED_TARGET: Target '{target}' not permitted for tool '{tool_id}'. Allowed: {contract.allowed_targets}"
            )

        return contract, runner
