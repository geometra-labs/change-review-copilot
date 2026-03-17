import { getToken } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function notImplemented<T>(message: string): Promise<T> {
  return Promise.reject(new Error(message));
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = typeof window !== "undefined" ? getToken() : null;

  const headers = new Headers(init?.headers || {});
  const body = init?.body;
  if (!(body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed with status ${res.status}`);
  }

  return res.json();
}

export const api = {
  auth: {
    register: (body: { email: string; password: string }) =>
      apiFetch<{ access_token: string; token_type: string }>("/auth/register", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    login: (body: { email: string; password: string }) =>
      apiFetch<{ access_token: string; token_type: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    me: () => apiFetch<{ id: string; email: string }>("/auth/me"),
  },
  projects: {
    list: () =>
      apiFetch<{ items: { id: string; name: string; description?: string | null; created_at: string }[] }>(
        "/projects"
      ),
    get: (id: string) =>
      apiFetch<{
        id: string;
        name: string;
        description?: string | null;
        created_at: string;
        model_versions?: {
          id: string;
          label: string;
          source_type: string;
          parse_status: string;
          created_at: string;
        }[];
      }>(`/projects/${id}`),
    create: (body: { name: string; description?: string }) =>
      apiFetch<{ id: string; name: string; description?: string | null; created_at: string }>("/projects", {
        method: "POST",
        body: JSON.stringify(body),
      }),
  },
  assemblies: {
    list: (_projectId: string) =>
      notImplemented<{ assemblies: { id: string; name: string; source: string }[] }>(
        "Assembly UI is not wired to the current backend yet."
      ),
    create: (_projectId: string, _body: { name: string; source: "upload" | "onshape"; external_id?: string }) =>
      notImplemented<{ id: string; name: string; source: string; project_id: string; created_at: string }>(
        "Assembly UI is not wired to the current backend yet."
      ),
  },
  changeEvents: {
    list: (_projectId: string, _assemblyId: string) =>
      notImplemented<{
        change_events: {
          id: string;
          change_type: string;
          component_id: string | null;
          description: string | null;
          created_at: string;
        }[];
      }>("Change event UI is not wired to the current backend yet."),
    create: (
      _projectId: string,
      _assemblyId: string,
      _body: { change_type: string; component_id?: string; description?: string }
    ) =>
      notImplemented<{
        id: string;
        change_type: string;
        component_id: string | null;
        description: string | null;
        created_at: string;
      }>("Change event UI is not wired to the current backend yet."),
  },
  impact: {
    generate: (_projectId: string, _assemblyId: string, _changeEventId: string) =>
      notImplemented<{
        report_id: string;
        change_event_id: string;
        warnings: {
          id: string;
          level: string;
          category: string;
          message: string;
          component_id?: string;
          interface_id?: string;
        }[];
        affected_component_ids: string[];
        inspect_next: string[];
      }>("Impact report UI is still on the older prototype flow."),
    get: (_projectId: string, _assemblyId: string, _reportId: string) =>
      notImplemented<{
        report_id: string;
        change_event_id: string;
        warnings: {
          id: string;
          level: string;
          category: string;
          message: string;
          component_id?: string;
          interface_id?: string;
        }[];
        affected_component_ids: string[];
        inspect_next: string[];
      }>("Impact report UI is still on the older prototype flow."),
  },
};
