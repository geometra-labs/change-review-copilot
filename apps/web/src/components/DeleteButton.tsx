"use client";

import { useState } from "react";

type Props = {
  label?: string;
  onDelete: () => Promise<void>;
};

export default function DeleteButton({ label = "Delete", onDelete }: Props) {
  const [busy, setBusy] = useState(false);

  async function handleClick() {
    const confirmed = window.confirm("Are you sure you want to delete this?");
    if (!confirmed) {
      return;
    }

    try {
      setBusy(true);
      await onDelete();
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={busy}
      style={{
        color: "white",
        background: "#dc2626",
        border: "none",
        padding: "6px 10px",
        borderRadius: 6,
      }}
    >
      {busy ? "Deleting..." : label}
    </button>
  );
}
