"use client";

import { useState } from "react";

type Props = {
  evidence: Record<string, unknown>;
};

export default function EvidenceDrawer({ evidence }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div>
      <button onClick={() => setOpen((value) => !value)}>
        {open ? "Hide Evidence" : "Show Evidence"}
      </button>
      {open ? (
        <pre
          style={{
            marginTop: 8,
            padding: 12,
            border: "1px solid #ddd",
            borderRadius: 8,
            background: "#f8f8f8",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          {JSON.stringify(evidence, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}
