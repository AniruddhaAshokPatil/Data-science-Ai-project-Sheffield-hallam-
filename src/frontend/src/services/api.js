const DEFAULT_TIMEOUT_MS = 12000;
const BASE = import.meta.env.VITE_API_BASE || '/api';

// I keep one shared request helper so every frontend API call uses the same
// base URL, headers, and error handling style.
async function request(path, options = {}) {
  const controller = new AbortController();
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
    signal: controller.signal
  }).catch((error) => {
    if (error.name === 'AbortError') {
      throw new Error('The request timed out before the API responded.');
    }
    throw error;
  });
  window.clearTimeout(timeoutId);

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`HTTP ${res.status}: ${txt}`);
  }
  return res.json();
}

export const api = {
  // I expose tiny wrapper methods so components can call api.get or api.post
  // without repeating fetch setup details in many files.
  get: (path, options) => request(path, options),
  post: (path, body, options) =>
    request(path, { method: 'POST', body: JSON.stringify(body), ...options })
};
