# Code Execution & Publishing Ecosystem Overview

This project provides three complementary layers for authoring, governing, and consuming code & ML logic:

| Layer | Purpose | Typical User | Key Features | Primary UI |
|-------|---------|-------------|--------------|------------|
| VS Terminal | Rapid ad-hoc coding, LLM assistance, report building | Analyst / Coder | In-browser editor, run snippets, capture matplotlib plots, chat with LLM, save & export markdown reports, AI provider selection | `/vs_terminal` |
| Secure Published Models | Controlled function-level publishing (allowed functions, edit requests) | Author & Consumers | Versioned publish, allowed function whitelist, run with args/kwargs + timeout, edit access requests & approvals | Sidebar panel inside `/vs_terminal` + `published_catalog.html` |
| Code Artifacts Governance | Full artifact lifecycle (version history, permissions, run request workflow, diff, rollback, starring, activity audit) | Author (coder) & Investor (consumer) | Versioned code snapshots, permission grants, run requests & approvals, diff & rollback, activity log, consolidated dashboards | `/code_artifacts`, `/code_artifact?slug=...` |

## When to Use Which
- Prototype quickly or draft reports: **VS Terminal**.
- Share a callable API-like function set with explicit allowed entrypoints: **Published Models**.
- Maintain governed code with history, permissions, and auditable run workflow: **Code Artifacts**.

## Role-Based Flow Summary
### Coder / Author
1. Draft code in VS Terminal → iterate rapidly.
2. Publish to governance layer: create a Code Artifact (dashboard New Artifact) or Published Model (publish panel) depending on control needs.
3. Grant permissions (view/run/edit/admin) on artifacts.
4. Review & approve run requests; execute approved requests; monitor activity.

### Investor / Consumer
1. Browse artifacts at `/code_artifacts` (visibility + permission filtered).
2. Open artifact detail to view code & metadata.
3. Submit run request with parameters (await approval & execution unless auto-approved by author running themselves).
4. Track personal run requests & authors' pending approvals via side panels.
5. Star interesting artifacts.

## Key APIs (Artifacts)
| Action | Method & Path | Notes |
|--------|---------------|-------|
| Create artifact | POST `/api/code/artifacts` | {title, code, visibility, ...} auto-slug |
| List artifacts | GET `/api/code/artifacts?page=&page_size=&q=&visibility=` | Returns effective_perms & starred |
| Get artifact | GET `/api/code/artifacts/<slug>?versions=1` | Include versions optionally |
| Update (new version) | PATCH `/api/code/artifacts/<slug>` | code + changelog => new version |
| Permissions list | GET `/api/code/artifacts/<slug>/permissions` | View if can_view |
| Set permission | POST `/api/code/artifacts/<slug>/permissions` | Requires can_edit/admin |
| Star / Unstar | POST `/api/code/artifacts/<slug>/(star|unstar)` | Idempotent toggle |
| Run request create | POST `/api/code/artifacts/<slug>/run_request` | Always starts pending |
| List run requests | GET `/api/code/artifacts/<slug>/run_requests` | Artifact scope |
| Decide (approve/reject) | POST `/api/code/run_requests/<id>/decide` | Requires can_edit |
| Execute approved | POST `/api/code/run_requests/<id>/execute` | Rate limited (5/hr unless editor) |
| Versions list | GET `/api/code/artifacts/<slug>/versions` | Metadata only |
| Diff versions | GET `/api/code/artifacts/<slug>/diff?from=&to=` | Unified diff list |
| Rollback | POST `/api/code/artifacts/<slug>/rollback` | Creates new version cloning target |
| Activity log | GET `/api/code/artifacts/<slug>/activities` | Latest 200 events |
| My run requests | GET `/api/code/my_run_requests` | Consolidated personal view |
| My pending approvals | GET `/api/code/my_pending_run_approvals` | Requests user can approve |

## Key APIs (Published Models)
(See `VS_TERMINAL_README.md` for full detail)
- Publish: POST `/api/publish_model`
- List: GET `/api/published_models`
- Public list: GET `/api/public/published_models`
- Detail: GET `/api/published_models/<id>`
- Run allowed function: POST `/api/published_models/<id>/run`
- Request edit: POST `/api/published_models/<id>/request_edit`
- View requests: GET `/api/published_models/<id>/requests`
- Decide request: POST `/api/published_models/<id>/requests/<rid>/decision`

## VS Terminal Highlights
- Run arbitrary Python: POST `/api/run_code` (optional plot capture)
- Save model file: POST `/api/save_model_code`
- Legacy publish: POST `/api/publish_model_legacy`
- LLM chat: POST `/api/vs_terminal/chat`
- Chat sessions: save/load `/api/vs_terminal/save_chat`, `/api/vs_terminal/chat_sessions`, `/api/vs_terminal/load_chat`
- Reports: save/list/load/delete/download/export endpoints (`/api/vs_terminal/*report*`)
- AI Providers dynamic configuration (`/api/ai/providers*`).

## Permission Matrix (Artifacts)
| Role/Perm | View | Run | Edit | Admin (same as edit placeholder) |
|-----------|------|-----|------|----------------------------------|
| Author | ✓ | ✓ | ✓ | ✓ |
| Granted can_view | ✓ | - | - | - |
| Granted can_run | ✓ | ✓ | - | - |
| Granted can_edit/admin | ✓ | ✓ | ✓ | ✓ |

Visibility adds baseline view: `public` (all), `internal` (any authenticated), `private` (only author + explicit grant).

## Activity Events
`create`, `update_version`, `update_meta`, `grant_perm`, `run_request`, `run_decision`, `run_execute`, `rollback`, `star`, `unstar`.

## Run Execution Safeguards
- Temp directory per execution, deleted after run.
- Best-effort resource limits (CPU 5s, ~256MB) on POSIX platforms.
- 30s timeout; status recorded.
- Basic per-user per-artifact rate limit (5/hr) for non-editors.

## Star / Unstar Semantics
- Star: increments global star count (idempotent if already starred).
- Unstar: removes user star and decrements count (never below zero).

## Side Panels (Dashboard)
- My Run Requests: personal lifecycle tracking across artifacts.
- Pending Approvals: actionable queue for editors to approve/execute.

## Recommended Workflow
1. Prototype in VS Terminal; commit stable logic as Code Artifact.
2. Use diff & versions to review changes before granting broader permissions.
3. Investors submit parameterized run requests; authors approve & execute.
4. Promote frequently used stable functions to Published Models for controlled invocation.

## Related Documentation
- `CODE_ARTIFACT_SYSTEM_README.md` – deeper dive into artifact internals.
- `VS_TERMINAL_README.md` – detailed VS Terminal usage & AI provider setup.

---
Last updated: 2025-08-16
