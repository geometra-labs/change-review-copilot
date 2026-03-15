const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) throw new Error(await res.text().catch(() => res.statusText));
  return res.json();
}

export const api = {
  projects: {
    list: () => fetchApi<{ projects: { id: string; name: string; created_at: string }[] }>("/projects"),
    get: (id: string) =>
      fetchApi<{ id: string; name: string; created_at: string; assemblies?: { id: string; name: string; source: string }[] }>(
        `/projects/${id}`
      ),
    create: (name: string) =>
      fetchApi<{ id: string; name: string; created_at: string }>("/projects", {
        method: "POST",
        body: JSON.stringify({ name }),
      }),
  },
  assemblies: {
    list: (projectId: string) =>
      fetchApi<{ assemblies: { id: string; name: string; source: string }[] }>(
        `/projects/${projectId}/assemblies`
      ),
    create: (projectId: string, body: { name: string; source: "upload" | "onshape"; external_id?: string }) =>
      fetchApi<{ id: string; name: string; source: string; project_id: string; created_at: string }>(
        `/projects/${projectId}/assemblies`,
        { method: "POST", body: JSON.stringify(body) }
      ),
  },
  changeEvents: {
    list: (projectId: string, assemblyId: string) =>
      fetchApi<{ change_events: { id: string; change_type: string; component_id: string | null; description: string | null; created_at: string }[] }>(
        `/projects/${projectId}/assemblies/${assemblyId}/change-events`
      ),
    create: (
      projectId: string,
      assemblyId: string,
      body: { change_type: string; component_id?: string; description?: string }
    ) =>
      fetchApi<{ id: string; change_type: string; component_id: string | null; description: string | null; created_at: string }>(
        `/projects/${projectId}/assemblies/${assemblyId}/change-events`,
        { method: "POST", body: JSON.stringify(body) }
      ),
  },
  impact: {
    generate: (projectId: string, assemblyId: string, changeEventId: string) =>
      fetchApi<{
        report_id: string;
        change_event_id: string;
        warnings: { id: string; level: string; category: string; message: string; component_id?: string; interface_id?: string }[];
        affected_component_ids: string[];
        inspect_next: string[];
      }>(`/projects/${projectId}/assemblies/${assemblyId}/impact`, {
        method: "POST",
        body: JSON.stringify({ change_event_id: changeEventId }),
      }),
    get: (projectId: string, assemblyId: string, reportId: string) =>
      fetchApi<{
        report_id: string;
        change_event_id: string;
        warnings: { id: string; level: string; category: string; message: string; component_id?: string; interface_id?: string }[];
        affected_component_ids: string[];
        inspect_next: string[];
      }>(`/projects/${projectId}/assemblies/${assemblyId}/impact/${reportId}`),
  },
};
