# Copy into a fresh review context

Review the specified SatQuery ticket against its requirement, base commit and candidate diff. Read AGENTS.md and the affected public contracts. Do not treat the author's explanation as proof. Run the smallest meaningful reproduction and check downstream consumers where interfaces changed.

Prioritise incorrect scientific semantics, source/preview confusion, named binding mistakes, parameter bypass, stale evidence, unsafe file decoding, authentication/authorization gaps, idempotency and error handling. Confirm mocks cannot masquerade as real results. Inspect changed tests for weakened expectations and fixtures for label leakage.

Return actionable findings with path/function, reproduction, impact and suggested correction. Distinguish observed defects, plausible risks and checks not performed. If no issue is found, state the review scope and remaining limits. Do not merge, deploy or rewrite unrelated code.
