# Code Artifact Publishing & Execution System

This document explains how code authors and other users interact with the Code Artifact system: publishing code, versioning, permissions, run requests, execution, and auditing.

## Feature Overview
- Artifact creation with slug, title, visibility, and initial code
- Versioning: automatic version increments on updates, changelog, rollback support
- Diff between two versions
- Permissions (view / run / edit / admin) per user
- Visibility flag (public / internal / private) layered with explicit permissions
- Starring artifacts
- Run Requests workflow (submit → approve/reject → execute)
- Sandboxed (best‑effort) execution with time & memory limits
- Rate limiting (default: 5 executions/hour per user per artifact, editors/admins bypass)
- Activity log (last 200 events – creation, updates, permissions, stars, run lifecycle, rollback)

## Core Concepts
| Concept | Description |
|---------|-------------|
| Artifact | A publishable code unit (Python code) with metadata and a current version. |
| Version | Immutable snapshot of code + changelog; new version on each update or rollback. |
| Permission | Grants specific capabilities to a username. |
| Run Request | A request to execute current artifact code with optional parameters. |
| Activity | Audit record of key actions for traceability. |

## Roles & Capabilities
| Capability | Requires |
|------------|---------|
| View metadata/code | Visibility allows OR explicit can_view |
| Star | View |
| Submit run request | View |
| Approve / Reject run request | Edit or Admin |
| Execute approved request | Run (auto-approve if user also Edit) |
| Update code (new version) | Edit |
| Grant / modify permissions | Admin |
| Rollback | Edit |
| Diff versions | View |

## Visibility vs Permissions
- `public`: Everyone can view (no permission record needed)
- `internal`: (If implemented) Limited to authenticated users (plus explicit grants) – treat as project-level
- `private`: Only explicit permissions grant access

Explicit permissions can further elevate (run/edit/admin) regardless of visibility.

## Run Request Lifecycle
1. Viewer submits request with optional JSON parameters
2. Status = `pending`
3. Editor/Admin decides: `approve` or `reject`
4. Approved request can be executed (execution may self‑approve if submitted by an editor)
5. Execution captures stdout/stderr, status → `executed`

Rate limiting rejects executions over threshold (429) for non-editors.

## Activity Events (examples)
- `create_artifact`
- `update_code`
- `grant_permission`
- `star`
- `run_request`
- `run_decision`
- `run_execute`
- `rollback`

Each includes `username`, timestamp, and metadata like version, request_id, success flags.

## Front-End Page (`/code_artifact?slug=...`)
Tabs:
1. Code: edit & save new version (with changelog)
2. Versions: list, diff, rollback
3. Run: submit run request and view last execution output
4. Permissions: grant/update permissions & list existing
5. Run Requests: manage pending/approved requests (approve/reject/execute)
6. Activity: recent audit trail

UI Enhancements:
- Toast notifications for actions
- Spinner overlay for async calls
- Badges for request status (pending/approved/executed/rejected)

## API Reference (JSON)
(Headers: `X-User: <username>`)

Artifacts:
- POST `/api/code/artifacts` {slug,title,visibility,code} → create
- GET `/api/code/artifacts/<slug>?versions=1` → artifact (optionally includes recent versions)
- PATCH `/api/code/artifacts/<slug>` {code?, changelog?, visibility?} → new version if code changes

Permissions:
- POST `/api/code/artifacts/<slug>/permissions` {username, can_view, can_run, can_edit, can_admin}
- GET `/api/code/artifacts/<slug>/permissions`

Starring:
- POST `/api/code/artifacts/<slug>/star`

Versions & Diff:
- GET `/api/code/artifacts/<slug>/versions`
- GET `/api/code/artifacts/<slug>/diff?from=X&to=Y`
- POST `/api/code/artifacts/<slug>/rollback` {version}

Run Requests:
- POST `/api/code/artifacts/<slug>/run_request` {params?}
- GET `/api/code/artifacts/<slug>/run_requests`
- POST `/api/code/run_requests/<id>/decide` {decision: approve|reject}
- POST `/api/code/run_requests/<id>/execute`

Activities:
- GET `/api/code/artifacts/<slug>/activities`

## Typical Author Workflow
1. Create artifact (POST) or via internal UI form
2. Share slug with collaborators
3. Grant permissions (run/edit) to selected users
4. Update code & provide changelog; versions accumulate
5. Review run requests (Run Requests tab) → approve or reject
6. Execute approved requests (or self-execute if editor)
7. Monitor Activity tab for auditing
8. Use Diff or Rollback as needed

## Typical Viewer / Runner Workflow
1. Open artifact page (if visible / permitted)
2. Star or review code/version history
3. Submit run request with parameters
4. Await approval; once approved and executed, view output

## Security & Safeguards
- Execution occurs in temp directory with time (≤30s) and memory (≈256MB, POSIX only) limits
- Basic rate limiting (5 runs/hour/user/artifact) for non-editors
- Rollback produces a new immutable version; history preserved
- Activity log provides audit trail

## Error Responses
Standard JSON: `{ ok: false, error: "message" }` with appropriate HTTP status (403 forbidden, 404 not found, 400 validation, 429 rate limit, 408 timeout, 500 internal).

## Extension Ideas
- Full sandbox (seccomp / container)
- Full-text search across code & changelogs
- Tagging & categories
- Scheduled executions
- Comment threads / code reviews
- WebSocket push for real-time request status

## Quick Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| 403 Forbidden | Missing permission | Grant view/run/edit/admin | 
| 429 Rate limit | Too many executions | Wait or elevate permissions |
| 408 Timeout | Long-running code | Optimize or raise limit safely |
| Empty versions list | No updates yet | Save a new version via PATCH |

## Minimal Example (Create + Run Request)
1. Create:
```
POST /api/code/artifacts
{"slug":"example_calc","title":"Example Calc","visibility":"public","code":"print('hello')"}
```
2. Submit run request:
```
POST /api/code/artifacts/example_calc/run_request
{"params": {"x":1}}
```
3. Approve & Execute (as editor):
```
POST /api/code/run_requests/123/decide {"decision":"approve"}
POST /api/code/run_requests/123/execute
```

## Data Model (Simplified)
- CodeArtifact(id, slug, title, visibility, current_version_id, stars, views, run_count, created_at, updated_at)
- CodeArtifactVersion(id, artifact_id, version, code, changelog, checksum, created_at, created_by)
- CodeArtifactPermission(id, artifact_id, username, can_view, can_run, can_edit, can_admin)
- CodeArtifactStar(id, artifact_id, username, created_at)
- CodeRunRequest(id, artifact_id, requester, status, params_json, decided_at, decided_by, run_started_at, run_finished_at, execution_output, execution_error)
- CodeArtifactActivity(id, artifact_id, event, username, metadata_json, created_at)

---
This README will evolve as new governance & security features are added.
