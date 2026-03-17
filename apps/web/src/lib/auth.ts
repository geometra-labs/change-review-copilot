"use client";

const TOKEN_KEY = "crc_token";
const LEGACY_TOKEN_KEY = "crc_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY) ?? window.localStorage.getItem(LEGACY_TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.removeItem(LEGACY_TOKEN_KEY);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(LEGACY_TOKEN_KEY);
}

// Backward-compatible aliases while older pages are phased out.
export const getStoredToken = getToken;
export const setStoredToken = setToken;
export const clearStoredToken = clearToken;
