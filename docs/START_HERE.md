# Start here: one coordinator, small parallel tasks

## 1. Machine A: Aryan's integration machine
Use one project folder outside OneDrive/Dropbox. Install Git, GitHub Desktop if a GUI helps, Python 3.12, and Node 24 from their official sites. A GPU is not needed for the contract/API/UI foundation. Linux containers or WSL may be useful for GIS/model workers later; do not install every model environment on every laptop.

Use uv 0.12.10 with Python 3.12 so installation is reproduced from `uv.lock`. On Windows PowerShell:
```powershell
py -3.12 -m pip install uv==0.12.10
uv sync --locked --extra dev --python 3.12
uv run --locked --extra dev python -m ruff check .
uv run --locked --extra dev python scripts\check.py
uv run --locked --extra dev python scripts\export_schemas.py
git diff --exit-code -- schemas
```

On macOS/Linux or WSL:
```bash
curl -LsSf https://astral.sh/uv/0.12.10/install.sh -o /tmp/uv-install.sh
sh /tmp/uv-install.sh
uv --version
uv python install 3.12
uv lock --check --python 3.12
uv sync --locked --extra dev --python 3.12
uv run --locked --extra dev python -m ruff check .
uv run --locked --extra dev python scripts/check.py
uv run --locked --extra dev python scripts/export_schemas.py
git diff --exit-code -- schemas
```

By default, `uv sync` and `uv run` manage the project's `.venv` and may replace an
incompatible environment. To preserve an existing `.venv`, first choose and inspect a
different absolute path, then set it for every project command:
```bash
export UV_PROJECT_ENVIRONMENT=/absolute/path/to/a/separate-environment
test ! -e "$UV_PROJECT_ENVIRONMENT" || readlink -f "$UV_PROJECT_ENVIRONMENT"
uv sync --locked --extra dev --python 3.12
uv run --locked --extra dev python scripts/check.py
```
Never point `UV_PROJECT_ENVIRONMENT` at an environment that has not been approved for
replacement or synchronization.

The lock and clean Python 3.12 installation were verified in WSL. A failed install must
be diagnosed before claiming the environment is ready. Do not mix Windows and WSL virtual environments.

Open the folder in Codex using your existing subscription. Start in planning/read-only mode for T01 diagnosis, then normal scoped editing for its implementation. Select the actual model from the model picker; use Sol high for the first engineering task. Ask it to read AGENTS.md and `prompts/INTEGRATOR.md`. Use Astra for architecture/contract decisions and difficult review, not formatting every file.

## 2. Establish Git before parallel work
Create a private repository using GitHub Desktop or GitHub's interface. Prefer a new clearly named repository for this starter until the teammate's existing repository is inspected. Do not replace their root files blindly. Add only source, documentation, small synthetic fixtures and schema exports; never data/checkpoints/secrets.

GitHub Desktop can add the local folder, initialise Git if needed, commit the starter, and publish the private repository. Each human teammate uses their own account; do not share credentials or API keys. Restrict repository access to the required people. Exact access/branch-protection features depend on the account plan. If an enforcement feature is unavailable, one integrator still owns merges and explicitly checks the gate; do not call an unenforced rule protected.

Connect only this repository in Codex cloud's environment setup if you want cloud tasks or PR reviews. A local Codex session can work without that connector. GitHub review is optional: after setup and access confirmation, `@codex review` on a PR requests a review. Account access and quota are not guaranteed by this package. Do not run every review twice through two paid services.

## 3. Machines B and C: Contributor workspaces
Do not give Contributor agents a clone of a sensitive main repository. The integrator prepares a fresh sanitised Git repository/export containing only approved contracts, UI specifications, public examples, synthetic data and ticket files. It must have no private history, hidden inputs, secrets or raw scientist feedback. A prompt saying 'ignore private files' is not a boundary. Restricted data stays off the machine/session or outside its genuinely enforced access scope.

Install OpenCode from its official instructions. Run `opencode`, then `/connect` and `/models`. If using Muse Spark 1.3 Contributor Free, acknowledge its data-use terms deliberately. Select high effort if offered; available variants depend on provider/model. Use `prompts/UI_WORKER.md` on B and `prompts/QA_WORKER.md` on C. Do not run `/init` to regenerate the shared project rules on each machine.

Worker branch names are assigned centrally, e.g. `t09-ui-b-01`; never let identical agents independently choose generic branch names. If workers share a fully public-safe repository, normal PRs are convenient. If working in a separate sanitised export, return a patch/commit plus handoff for review and import; do not merge its unrelated history into the main project.

## 4. Optional machine D
Do not buy Go merely because another laptop exists. First run one bounded trial ticket. If limits or a private implementation lane become the bottleneck, consider one $10/month Go seat. Its current documentation has model-specific quotas and privacy differences. Buying Go does not make Muse Contributor private. Trial a listed non-Contributor coding model on the same task, then select by correctness and repair effort. Disable Use balance and automatic balance reload for bounded spending.

Use `prompts/SPECIALIST_WORKER.md` for a real adapter ticket if the data/provider conditions permit. Otherwise D runs independent reproductions or approved public-data research. More machines stay idle until there are independent ready tasks. Laptops do not pool their GPUs automatically.

## 5. Routine daily loop
1. Integrator chooses ready tickets, records base commit and contract version, assigns file ownership.
2. Each worker reads the small context package, confirms scope, reproduces the baseline and implements one behaviour slice.
3. Worker runs relevant checks and sends a handoff using the template.
4. Reviewer starts a fresh context with requirement, diff and evidence. Important claims are reproduced, not accepted from a summary.
5. Integrator merges one reviewed change, runs integrated checks on the new commit, updates STATUS.md and releases dependent tickets.

Use one owner-only status file and per-ticket handoffs. No agent chat bus is needed. Send updates at session start, blocker, interface proposal, handoff and merge; not after every small edit. If you manually carry messages, carry the commit SHA and concrete artifact paths as well as prose. No shared-memory magic exists across unrelated chats or laptops.

Same-machine parallel work uses a separate Git worktree per session; different laptops use separate clones. Worktrees do not solve private-data exposure because they share repository history. Do not use unrestricted/auto-approve settings as a substitute for a scoped environment. Routine edits/tests inside an assigned disposable checkout may be preauthorised; deployment, spending, credentials and external messages stay separate.

## 6. Dependencies and MCP
Required initially: Git/repository, Python/Pydantic, the chosen coding client; Node/React tooling when UI starts. Required for real analysis: compatible GIS/model environment, legitimate datasets/checkpoints and adequate GPU access. A runtime language-model provider or local model is separate from the coding subscription. API keys go in environment/secret storage, never chat or Git.

Optional: GitHub connection for PRs, browser/Playwright for UI tests, official documentation MCP if useful. No Figma, paid review service, OpenClaw, Hermes, autonomous research fleet or third-party GIS MCP is required. Prefer direct registered GIS functions in the product. In this delivery no repo connection, purchase or deployment has been performed.

Sources: [Codex cloud](https://learn.chatgpt.com/docs/cloud), [Codex worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees), [Codex GitHub review](https://learn.chatgpt.com/docs/third-party/github), [OpenCode rules](https://opencode.ai/docs/rules/), [OpenCode models](https://opencode.ai/docs/models/), [OpenCode Go](https://opencode.ai/docs/go/), [OpenCode Zen](https://opencode.ai/docs/zen/). Checked 6 September 2026. Setup commands should be verified on the installed clients.
