import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <h1>CAD Change-Impact Copilot</h1>
      <p>Analyze impact of design changes on your assembly.</p>
      <p>
        <Link href="/projects">View projects</Link> · <Link href="/projects/new">New project</Link>
      </p>
    </main>
  );
}
