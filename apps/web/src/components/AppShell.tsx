"use client";

import type { ReactNode } from "react";
import Link from "next/link";

import LogoutButton from "./LogoutButton";
import RequireAuth from "./RequireAuth";

type Props = {
  children: ReactNode;
};

export default function AppShell({ children }: Props) {
  return (
    <RequireAuth>
      <div style={{ minHeight: "100vh" }}>
        <header
          style={{
            padding: 16,
            display: "flex",
            justifyContent: "space-between",
            borderBottom: "1px solid #ddd",
          }}
        >
          <nav style={{ display: "flex", gap: 16 }}>
            <Link href="/projects">Projects</Link>
          </nav>
          <LogoutButton />
        </header>
        <main>{children}</main>
      </div>
    </RequireAuth>
  );
}
