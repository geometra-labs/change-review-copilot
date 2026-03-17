import Link from "next/link";

export default function HomePage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Change Review Copilot</h1>
      <p>Geometry-first assembly change review.</p>
      <p>
        <Link href="/login">Go to Login</Link>
      </p>
    </main>
  );
}
