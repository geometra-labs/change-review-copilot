import type { Metadata } from "next";
import "./global.css";

export const metadata: Metadata = {
  title: "CAD Change-Impact Copilot",
  description: "Geometry-aware assembly change-impact analysis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
