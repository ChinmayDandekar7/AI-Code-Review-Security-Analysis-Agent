# AI Code Review & Security Analysis Agent — Frontend

React + Vite UI for the Code Submission Module and Knowledge Base search,
styled as a VS Code–inspired editor interface (tab strip, line-numbered
code pane, status bar) since that's where developers actually live.

## Setup

```bash
npm install
cp .env.example .env    # adjust VITE_API_BASE if your backend runs elsewhere
npm run dev
```

Open **http://localhost:5173**. The backend (see `../backend/README.md`) must
be running on port 8000 for requests to succeed — the connection dot in the
top-right corner shows live status.

## What's here

| View | What it does |
|---|---|
| Submit Code → Paste | Editor-style textarea with line-number gutter, **live auto-detected language badge** (no manual selection needed), syntax validation results |
| Submit Code → Upload | Drag-and-drop `.py`/`.java` file upload |
| Knowledge Base | Search the indexed OWASP/secure-coding knowledge base directly |

## Structure

```
src/
  App.jsx                    # top-level layout and state
  api.js                      # fetch wrappers for the backend
  components/
    TitleBar.jsx               # editor chrome + backend connection status
    TabStrip.jsx                # reusable tab switcher
    CodeEditor.jsx               # textarea + synced line-number gutter
    UploadZone.jsx                # drag-and-drop file upload
    ResultsPanel.jsx               # validation results (Problems-panel style)
    KnowledgeBasePanel.jsx          # RAG search UI
    StatusBar.jsx                    # bottom status bar
  styles/tokens.css            # design tokens (colors, type, spacing)
```

## Build for production

```bash
npm run build
```

Output goes to `dist/`.
