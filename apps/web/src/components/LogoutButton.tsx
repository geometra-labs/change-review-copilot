"use client";

import { useRouter } from "next/navigation";

import { clearToken } from "@/lib/auth";

export default function LogoutButton() {
  const router = useRouter();

  return (
    <button
      onClick={() => {
        clearToken();
        router.replace("/login");
      }}
    >
      Logout
    </button>
  );
}
