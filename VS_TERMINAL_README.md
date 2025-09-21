# VS Terminal & Multi-Provider AI Integration

An embedded VS Code–style research & coding workspace inside the application that lets you:

- Run arbitrary Python snippets in a sandboxed subprocess
- Capture matplotlib plots automatically (Charts tab)
- Build rich analytical reports (markdown) with embedded plots & uploaded images
- Export reports to styled HTML and PDF (with images, code blocks, lists, tables)
- Maintain persistent chat sessions (save / load) + link chat content into reports
- Integrate with multiple external Large Language Model (LLM) API providers (free & paid)
- Seamlessly switch between a local/hosted default model and external providers

---
## 1. Feature Overview

| Area | Capabilities |
|------|--------------|
| Code Execution | Subprocess isolation, stdout/stderr capture, optional plot capture flag |
| Plot Handling | Auto-extracts figure PNGs (base64) -> Charts tab -> insert individually or bulk into report |
| Reporting | Markdown editor + live preview; autosave draft; embed code output, charts, images, chat replies |
| Media Embeds | `![Alt](data:image/png;base64,...)` in markdown for charts & uploaded images |
| Export | `/api/vs_terminal/export_report_html` (styled HTML) & `/api/vs_terminal/export_report_pdf` (ReportLab) |
| Chat | Contextual coding help; add AI replies to report with one click |
| Sessions | Save & reload chat sessions (JSON) including active report markdown snapshot |
| Providers | Configure & select external AI APIs: OpenAI, Anthropic, Gemini, HuggingFace, Cohere, Mistral, OpenRouter, Azure OpenAI, Perplexity |
| Persistence | Reports stored in `reports/generated/*.md`; provider config in `provider_config.json` |

---
## 2. File & Module Map

| File | Purpose |
|------|---------|
| `templates/vs_terminal.html` | Frontend workspace UI (editor, tabs, sidebar, chat, provider panel) |
| `llm_providers.py` | Unified adapter for all supported AI providers |
| `app.py` | Flask endpoints (code run, report CRUD, export, provider management) |
| `provider_config.json` | (Generated) Stores per-provider API keys / model names (DO NOT COMMIT) |

---
## 3. Supported AI Providers

Key added providers (all optional):

- OpenAI
- Anthropic (Claude)
- Google Gemini
- HuggingFace Inference API
- Cohere
- Mistral AI
- OpenRouter (meta-gateway)
- Azure OpenAI (custom base URL + deployment name)
- Perplexity (Sonar models)

Each provider entry tracks: `api_key`, optional `model`, and for Azure: `base_url`.

### 3.1 Environment Strategy
- Primary storage: `provider_config.json` (plaintext; treat as secret; exclude from VCS)
- Alternative: Set env vars and extend `llm_providers.py` to reference them (e.g. `OPENAI_API_KEY`).

---
## 4. Security & Secret Handling

| Risk | Mitigation |
|------|------------|
| Plaintext key storage | Keep `provider_config.json` out of version control; set restrictive file permissions |
| Key leakage in logs | Code avoids logging full keys; do not add debug prints of config |
| Browser exposure | Keys only posted once and never re-sent to client after save |
| Rotation | Overwrite with new key in Configure Provider form or delete JSON and restart |

**Production Recommendation:** Replace flat-file with a secrets manager (AWS Secrets Manager / Parameter Store / Vault) and adapt load/save functions.

---
## 5. Backend Endpoints (Provider Layer)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/providers` | List supported providers + configured state |
| POST | `/api/ai/providers/configure` | Body: `{provider, api_key?, model?, base_url?}` Save credentials / model |
| POST | `/api/ai/providers/select` | Body: `{provider, model?}` Set active provider runtime state |
| POST | `/api/ai/chat` | Body: `{provider, model?, messages:[{role, content}]}` Returns `{reply}` |

Message roles: `user`, `assistant`, `system` (some providers ignore `system`).

---
## 6. Frontend Workflow

1. Open sidebar section "AI PROVIDERS".
2. Click **Refresh** to fetch provider list.
3. Pick a provider in the dropdown.
4. Enter API Key (and Model, if you want to force a non-default).
5. (Azure only) supply `Base URL` like `https://YOUR-RESOURCE-NAME.openai.azure.com` (no trailing slash).
6. Click **Save Provider**.
7. Click **Select Active** to mark it active (enables focused usage in custom integrations or future auto-routing logic).
8. Use the existing Chat pane (currently still calling local `/api/vs_terminal/chat`). Optionally call `/api/ai/chat` directly in custom code for that provider.

> NOTE: The baseline chat UI still targets the local LLM client endpoint. To leverage external providers, either (a) add a toggle to switch endpoints or (b) integrate a new button that posts to `/api/ai/chat` and renders the reply. (Left minimal by design.)

---
## 7. Code Execution & Plot Capture

### 7.1 Running Code
- Press **Run** or use the run toolbar button.
- Optional: check **Plots** to capture matplotlib figures.
- Captured figures populate the **CHARTS** tab (auto-switch on success).

### 7.2 Adding Charts to Report
- Single chart: click **To Report** under the thumbnail.
- All charts: **All To Report** button.
- Charts appended as markdown image embeds.

### 7.3 Adding Raw Output / Chat
- Result output: **+ To Report** (from RESULT tab) or **Add Last Output** inside REPORT tab.
- Chat message block: Use the mini **To Report** button inside each AI reply.

---
## 8. Reporting System

| Action | How |
|--------|-----|
| Add Text | Type in markdown editor (`reportEditor`) |
| Live Preview | **Preview** toggle (re-click to return to edit) |
| Insert Code Output | Use **Add Last Output** or **+ To Report** |
| Insert Images | **Image** -> file picker (embeds as data URI) |
| Insert Charts | From CHARTS tab (single or bulk) |
| Save Report | **Save** -> supply filename (stored as `.md`) |
| Download | **Download** (after save) |
| Export HTML | **Export HTML** (selected saved report) |
| Export PDF | **Export PDF** (selected saved report) |

Autosave: Draft stored in `localStorage` every 5s under key `vst_report_draft`.

### 8.1 Markdown Subset Supported (Preview & Export)
- Headings: `#`, `##`, `###`
- Lists: `-`, `*`, `+`, numbered
- Code fences: ``` ```lang
- Inline code: \`code\`
- Tables: Pipe syntax (simplified)
- Images: `![alt](data:image/png;base64,...)`
- Bold / Italic: `**bold**`, `*italic*`

---
## 9. PDF Export Notes

Renderer: ReportLab
- Headings scaled (H1 > H2 > H3)
- Code blocks monospaced (Courier)
- Images auto-scaled to page width
- Lists recognized (bullets / ordered)
- Tables currently flattened to plain text (future enhancement)

---
## 10. Adding a New Provider (Extension Guide)

1. Update `SUPPORTED_PROVIDERS` in `llm_providers.py` with metadata.
2. Add a branch in `call_provider()` for the new provider.
3. (If custom base URL) mark `requires_base_url` True.
4. Restart app; provider auto-appears in UI.

---
## 11. AWS Deployment Considerations

If hosting an OpenAI-compatible gateway or Azure OpenAI:
- Base URL examples:
  - Azure: `https://my-az-openai.openai.azure.com`
  - Self-host (EC2 + reverse proxy): `https://llm.yourdomain.com`
- Do **not** include trailing slash or `/openai` segment.
- Ensure Security Group allows inbound 443; ALB / Nginx forwards to Flask or gateway.

Testing:
```
curl -I https://llm.yourdomain.com
```
Expect 200/301/302/404. For Azure the constructed path includes `/openai/deployments/<deployment>/chat/completions`.

---
## 12. provider_config.json Format

```json
{
  "providers": {
    "openai": {"api_key": "sk-...", "model": "gpt-4o"},
    "azure_openai": {"api_key": "<key>", "model": "myDeployment", "base_url": "https://resource.openai.azure.com"},
    "perplexity": {"api_key": "pplx-...", "model": "llama-3.1-sonar-small-128k-online"}
  }
}
```

Exclude this file from git commits.

---
## 13. Minimal Example: External Chat Call

```bash
curl -X POST http://localhost:5008/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "perplexity",
    "model": "llama-3.1-sonar-small-128k-online",
    "messages": [
      {"role": "user", "content": "Give a Python snippet that sums a list."}
    ]
  }'
```

Response:
```json
{"reply": "You can use sum(list_var) ..."}
```

---
## 14. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Provider shows `none` | No key saved | Configure -> Save Provider |
| 400 Unsupported provider | Typo in provider key | Use list from `/api/ai/providers` |
| 400 Model not specified | Model required for that provider | Add model in form or config file |
| Azure 404 | Base URL malformed | Remove trailing slash / duplicate path |
| Empty reply | Rate limit or error suppressed | Inspect server logs & raw JSON; add logging in branch |
| HTML export NameError (fixed) | CSS braces unescaped | Already resolved by template braces doubling |

---
## 15. Roadmap Ideas
- Toggle in chat pane to choose provider per message
- Streaming token updates (Server-Sent Events / WebSocket)
- Syntax highlighting in HTML export (highlight.js)
- Table rendering in PDF (grid layout)
- TOC generation for long reports
- Image size directives (e.g. `![alt|width=50%]()`)
- Secret vault integration

---
## 16. Quick Start Summary

1. Run the Flask app.
2. Open VS Terminal UI.
3. (Optional) Configure external provider + Select Active.
4. Write & run code; capture plots.
5. Build report: add outputs, charts, images, chat replies.
6. Save, then export HTML/PDF.

You're ready to produce rich, AI-assisted analytical reports.

---
**Disclaimer:** External model output may be inaccurate. Always validate financial or analytical conclusions.
