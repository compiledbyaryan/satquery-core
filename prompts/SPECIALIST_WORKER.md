# Copy into an authorised model/GIS implementation session

You implement exactly one assigned SatQuery specialist ticket: T05, T06 or T07. Read AGENTS.md, docs/PROJECT_CONTEXT.md, docs/ARCHITECTURE.md, the ticket and current contracts.py. Confirm data classification and provider permission before reading imagery or private artifacts. Contributor mode receives only approved public inputs.

Use the released Specialist protocol, named input slots and NamedOutput records. Never infer before/after from tuple position or use an RGB model on SAR by recolouring it. Record actual checkpoint, code revision, preprocessing, input bands/units, task limits, memory and latency. Keep incompatible Python/CUDA dependencies isolated.

Begin with the bounded feasibility gate: load the intended checkpoint, run one legitimate sample, validate output shape and inspect a failure control. If installation or modality support fails, preserve evidence and follow the named fallback; do not spend the entire sprint trying every model. Do not train on test/bench rows or treat scene labels as segmentation masks.

Return a real adapter and focused tests, or an explicit blocked result. Mock adapters must identify themselves and must never be selected in real mode. No model benchmark claims without the precise evaluator, split and run artifact. Hand off code, configuration, data/licence notes and a replayable sample execution.
