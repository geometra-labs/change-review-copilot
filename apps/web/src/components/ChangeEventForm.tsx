"use client";

import { useState } from "react";

const CHANGE_TYPES = [
  "dimension_changed",
  "part_replaced",
  "part_moved",
  "part_added_removed",
] as const;

interface ChangeEventFormProps {
  projectId: string;
  assemblyId: string;
  onSuccess: () => void;
}

export function ChangeEventForm({ projectId, assemblyId, onSuccess }: ChangeEventFormProps) {
  const [changeType, setChangeType] = useState<string>(CHANGE_TYPES[0]);
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { api } = await import("@/lib/api");
      await api.changeEvents.create(projectId, assemblyId, {
        change_type: changeType,
        description: description.trim() || undefined,
      });
      onSuccess();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create change event");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <div>
        <label htmlFor="changeType">Change type</label>
        <br />
        <select
          id="changeType"
          value={changeType}
          onChange={(e) => setChangeType(e.target.value)}
          disabled={loading}
          style={{ padding: "0.5rem", marginTop: "0.25rem" }}
        >
          {CHANGE_TYPES.map((typeValue) => (
            <option key={typeValue} value={typeValue}>
              {typeValue}
            </option>
          ))}
        </select>
      </div>
      <div style={{ marginTop: "0.75rem" }}>
        <label htmlFor="description">Description (optional)</label>
        <br />
        <input
          id="description"
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={loading}
          style={{ padding: "0.5rem", width: "20rem", marginTop: "0.25rem" }}
        />
      </div>
      {error && <p style={{ color: "red", marginTop: "0.5rem" }}>{error}</p>}
      <button type="submit" disabled={loading} style={{ marginTop: "1rem", padding: "0.5rem 1rem" }}>
        {loading ? "Creating..." : "Create change event"}
      </button>
    </form>
  );
}
