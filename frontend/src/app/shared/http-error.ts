export function detailOf(error: unknown, fallback: string): string {
  const detail = (error as {error?: {detail?: unknown}})?.error?.detail;
  if (typeof detail === "string" && detail.length > 0) {
    return detail;
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((d) => (d as {msg?: unknown})?.msg)
      .filter((m): m is string => typeof m === "string");
    if (messages.length > 0) {
      return messages.join(", ");
    }
  }
  return fallback;
}
