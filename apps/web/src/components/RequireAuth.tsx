"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getToken } from "@/lib/auth";

type Props = {
  children: ReactNode;
};

export default function RequireAuth({ children }: Props) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [router]);

  if (!ready) {
    return (
      <main style={{ padding: 24 }}>
        <p>Checking session...</p>
      </main>
    );
  }

  return <>{children}</>;
}
