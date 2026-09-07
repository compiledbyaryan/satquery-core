# Copy into Machine B's approved Contributor workspace

You implement SatQuery's map-first UI. This workspace must contain only material approved for Contributor data use. If it contains private history, secrets, scientist correspondence or restricted imagery, stop and ask the coordinator for a clean workspace; do not merely promise to ignore it.

Read AGENTS.md, docs/PROJECT_CONTEXT.md, docs/UI_SPEC.md, docs/ARCHITECTURE.md, your T09 ticket and the merged schema/transport exports. You have no prior conversation context. The product analyses single optical/SAR, temporal pairs and optical-SAR pairs, showing evidence, uncertainty and actual tool execution.

Allowed scope: apps/web/src, apps/web/tests and your handoff. Root dependencies, lockfiles and shared transport definitions belong to the integrator unless explicitly assigned. If T02/T03 transport is not merged, build only an isolated, clearly labelled fixture-based visual prototype; do not invent live routes or report integration complete.

Implement one workflow at a time: select inputs, ask query, show real run state, inspect a claim, reach evidence. Follow the Field Desk visual specification, including error/empty/partial/stale states and reduced motion. Do not add decorative nonfunctional controls or fake metrics. Impeccable may critique and polish if the coordinator installed it; avoid another design system.

Run the assigned TypeScript/unit/browser checks once tooling exists. Capture relevant screenshots at 1440 and 1024 widths and reduced motion. Report what is mocked, what is wired to the real API, and exact failures. Deliver only the assigned patch/branch and handoff.
