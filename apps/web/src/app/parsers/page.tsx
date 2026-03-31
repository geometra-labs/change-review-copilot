"use client";

import { useEffect, useState } from "react";

import AppShell from "@/components/AppShell";
import StatusBadge from "@/components/StatusBadge";
import { apiFetch } from "@/lib/api";

type Capability = {
  name: string;
  extensions: string[];
  supported: boolean;
  notes: string;
};

export default function ParsersPage() {
  const [items, setItems] = useState<Capability[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<{ items: Capability[] }>("/parsers/capabilities")
      .then((data) => setItems(data.items))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load capabilities"));
  }, []);

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <h1>Parser Capabilities</h1>
        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Extensions</th>
              <th>Supported</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.name}>
                <td>{item.name}</td>
                <td>{item.extensions.join(", ")}</td>
                <td><StatusBadge status={item.supported ? "completed" : "failed"} /></td>
                <td>{item.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
