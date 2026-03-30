"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { setToken } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function LoginPage() {
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password123");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const endpoint = mode === "login" ? "/auth/login" : "/auth/register";

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const data = await res.json();
      setToken(data.access_token);
      router.push("/projects");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <main style={{ padding: 24, maxWidth: 480 }}>
      <h1>{mode === "login" ? "Login" : "Register"}</h1>
      <p>Seeded demo account: demo@example.com / password123</p>
      <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          type="password"
        />
        <button type="submit">{mode === "login" ? "Login" : "Register"}</button>
      </form>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      <button onClick={() => setMode(mode === "login" ? "register" : "login")} style={{ marginTop: 12 }}>
        Switch to {mode === "login" ? "Register" : "Login"}
      </button>
    </main>
  );
}
