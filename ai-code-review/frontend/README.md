# AI Code Review & Security Analysis Agent — Frontend

React + Vite UI, styled as a VS Code-inspired editor interface (tab strip,
line-numbered code pane, status bar) since that's where developers actually
live. Covers both Milestone 1 (submission + knowledge base) and Milestone 2
(agent findings display).

## Setup

```bash
npm install
copy .env.example .env    # Windows; use `cp` on macOS/Linux
npm run dev
```

Open **http://localhost:5173**. The backend (see `../backend/README.md`)
must be running on port 8000 — the connection dot in the top-right shows
live status.

## What's here

| View | What it does |
|---|---|
| Submit Code -> Paste | Line-numbered editor, live auto-detected language badge, syntax validation |
| Submit Code -> Upload | Drag-and-drop .py/.java upload |
| Submit Code -> Run Analysis | After valid syntax, triggers Milestone 2 agents and shows severity-scored findings with remediation |
| Knowledge Base | Search the indexed OWASP/secure-coding knowledge base directly |

## Structure

```
src/
  App.jsx                       # top-level layout and state
  api.js                         # fetch wrappers for the backend
  components/
    TitleBar.jsx                  # editor chrome + backend connection status
    TabStrip.jsx                   # reusable tab switcher
    CodeEditor.jsx                  # textarea + synced line-number gutter
    UploadZone.jsx                   # drag-and-drop file upload
    LanguageBadge.jsx                 # live auto-detect badge
    ResultsPanel.jsx                   # syntax validation results
    FindingsPanel.jsx                   # Milestone 2 agent findings display
    KnowledgeBasePanel.jsx                # RAG search UI
    StatusBar.jsx                          # bottom status bar
  styles/tokens.css                # design tokens (colors, type, spacing)
```

## Build for production

```bash
npm run build
```
