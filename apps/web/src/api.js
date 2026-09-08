const API = "";

async function request(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || res.statusText);
  }
  return res.json();
}

export const api = {
  health: () => request("/api/health"),
  videos: () => request("/api/videos"),
  createVideo: (filename, loadingBay = "Bay-A") =>
    request("/api/videos", { method: "POST", body: JSON.stringify({ filename, loading_bay: loadingBay }) }),
  processVideo: (id) => request(`/api/videos/${id}/process`, { method: "POST" }),
  incidents: (params = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v))
    ).toString();
    return request(`/api/incidents${qs ? `?${qs}` : ""}`);
  },
  incident: (id) => request(`/api/incidents/${id}`),
  incidentReport: (id, fmt = "json") => request(`/api/incidents/${id}/report?fmt=${fmt}`),
  patchIncident: (id, body) =>
    request(`/api/incidents/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  summary: () => request("/api/analytics/summary"),
  assistant: (question) =>
    request("/api/assistant/query", { method: "POST", body: JSON.stringify({ question }) }),
  behaviours: () => request("/api/config/behaviours"),
  zones: () => request("/api/zones"),
};
