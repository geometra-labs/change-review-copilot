export async function pollUntil<T>(
  fn: () => Promise<T>,
  isDone: (value: T) => boolean,
  timeoutMs = 30000,
  intervalMs = 1000
): Promise<T> {
  const start = Date.now();

  while (true) {
    const value = await fn();
    if (isDone(value)) {
      return value;
    }

    if (Date.now() - start > timeoutMs) {
      throw new Error("Polling timed out");
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
}
