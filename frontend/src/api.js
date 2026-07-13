const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function handle(response) {
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join(", ")
      : detail || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}

export async function detectLanguage(code) {
  const form = new FormData();
  form.append("code", code);
  const res = await fetch(`${API_BASE}/submission/detect-language`, {
    method: "POST",
    body: form,
  });
  return handle(res);
}

export async function submitPastedCode(code, language = null) {
  const form = new FormData();
  form.append("code", code);
  if (language) form.append("language", language);
  const res = await fetch(`${API_BASE}/submission/paste`, {
    method: "POST",
    body: form,
  });
  return handle(res);
}

export async function submitUploadedFile(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/submission/upload`, {
    method: "POST",
    body: form,
  });
  return handle(res);
}

export async function searchKnowledgeBase(query, topK = 5) {
  const params = new URLSearchParams({ q: query, top_k: String(topK) });
  const res = await fetch(`${API_BASE}/knowledge/search?${params.toString()}`);
  return handle(res);
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/`);
  return handle(res);
}
