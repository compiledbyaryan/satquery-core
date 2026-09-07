# SatQuery build starter

This package contains the initial contract foundation and AI-worker instructions. **It is not yet a web application, inference server, trained model or scientist-ready release.**

Start with `docs/START_HERE.md`. The full build playbook is delivered separately as a PDF.

## Present and tested
- Pydantic v2 definitions for AssetRecord, ToolContract, PlanRecord, ExecutionEvent and ClaimRecord.
- Named tool inputs/outputs, typed parameter variants, and a specialist protocol.
- Pure guards for input slots, bands, modalities, time order, georeferencing presence, grid arithmetic and dependency invalidation.
- 42 tests executed successfully using Python 3.12. The unittest tests are also discoverable by pytest.
- Seven generated JSON Schemas, instructions, worker prompts and sequenced tickets.

## Run
With Python 3.12 and Pydantic 2.13.4 available:
```bash
python scripts/check.py
python scripts/export_schemas.py
```
For a clean environment, install the package first using the setup instructions. Dependencies other than Pydantic are not required for the baseline check. Full dev dependency installation, pytest execution, mypy and Ruff checks were not completed in the authoring environment because dependency installation was unavailable. The first ticket completes this gate and creates the dependency lock. Do not claim those checks passed.

## Required next work
The API, durable jobs, auth, raster decoding, geometry semantics, specialist execution, adaptation, GUI, exports and end-to-end evaluation are still to be implemented. Generated schemas validate structure; runtime code must establish metadata accuracy, registration, artifact ownership, permitted parameters, tool versions and evidence support. Benchmark identity supplied in a record must be checked against a server-side manifest, not trusted from a user string.

## Reading order
1. `docs/START_HERE.md` - machine setup and coordination.
2. `docs/PROJECT_CONTEXT.md` and `docs/ARCHITECTURE.md` - requirements and boundaries.
3. `docs/UI_SPEC.md` - design and interaction specification.
4. `docs/TICKETS.md` - order, owners, exact paths and acceptance tests.
5. `prompts/` - copy the appropriate worker prompt into a fresh session.

Do not add a remote or merge into a teammate's repository until its contents and ownership are inspected. Do not upload restricted imagery or checkpoints to Git. Sample fixtures in this starter are synthetic.

