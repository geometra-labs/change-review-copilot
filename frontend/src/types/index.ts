export interface Project {
  id: string;
  name: string;
  created_at: string;
  assemblies?: AssemblyRef[];
}

export interface AssemblyRef {
  id: string;
  name: string;
  source: string;
}

export interface Assembly {
  id: string;
  name: string;
  source: string;
  project_id: string;
  created_at: string;
}

export type ChangeType =
  | "dimension_changed"
  | "part_replaced"
  | "part_moved"
  | "part_added_removed";

export interface ChangeEvent {
  id: string;
  change_type: string;
  component_id: string | null;
  description: string | null;
  created_at: string;
}

export type WarningLevel = "high" | "medium" | "low";

export interface Warning {
  id: string;
  level: WarningLevel;
  category: string;
  message: string;
  component_id?: string | null;
  interface_id?: string | null;
}

export interface ImpactReportResponse {
  report_id: string;
  change_event_id: string;
  warnings: Warning[];
  affected_component_ids: string[];
  inspect_next: string[];
}
