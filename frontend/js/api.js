const API_BASE = "http://127.0.0.1:8000";
let loadingCount = 0;

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiFetch(path, options = {}) {
  setLoading(true);
  try {
    const resp = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...authHeaders(),
      },
    });
    if (!resp.ok) {
      const errorBody = await resp.text();
      throw new Error(errorBody || "Request failed");
    }
    const contentType = resp.headers.get("content-type") || "";
    if (contentType.includes("application/json")) return resp.json();
    return resp;
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  const overlay = document.getElementById("loadingOverlay");
  if (!overlay) return;
  loadingCount = isLoading ? loadingCount + 1 : Math.max(0, loadingCount - 1);
  overlay.style.display = loadingCount > 0 ? "flex" : "none";
}

function apiErrorMessage(err) {
  const msg = (err && err.message) || "Unknown error";
  if (msg.includes("OPENAI_API_KEY")) {
    return "OpenAI key is missing. Add OPENAI_API_KEY in .env for AI extraction.";
  }
  return msg.replace(/^"|"$/g, "");
}
