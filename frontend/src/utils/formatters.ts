export function formatNumber(num: number | undefined | null): string {
  if (num === undefined || num === null) return "0";
  return num.toLocaleString();
}

export function formatCompactNumber(num: number | undefined | null): string {
  if (num === undefined || num === null) return "0";
  if (num >= 1_000_000) {
    return (num / 1_000_000).toFixed(1) + "M";
  }
  if (num >= 1_000) {
    return (num / 1_000).toFixed(1) + "K";
  }
  return num.toString();
}

export function formatDurationMs(ms: number | undefined | null): string {
  if (ms === undefined || ms === null) return "0 ms";
  if (ms >= 1000) {
    return (ms / 1000).toFixed(1) + "s";
  }
  return ms.toFixed(1) + "ms";
}

/**
 * Formats a date value as DD-MM-YYYY (e.g. "18-08-2026").
 * Accepts string, Date, number, or null/undefined.
 */
export function formatDate(dateInput: string | Date | number | undefined | null): string {
  if (!dateInput) return "-";
  try {
    const d = typeof dateInput === "object" ? dateInput : new Date(dateInput);
    if (isNaN(d.getTime())) return String(dateInput);
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const year = d.getFullYear();
    return `${day}-${month}-${year}`;
  } catch {
    return String(dateInput);
  }
}

/**
 * Formats a date/timestamp as DD-MM-YYYY HH:mm or DD-MM-YYYY HH:mm:ss.
 */
export function formatDateTime(
  dateInput: string | Date | number | undefined | null,
  includeSeconds: boolean = false
): string {
  if (!dateInput) return "-";
  try {
    const d = typeof dateInput === "object" ? dateInput : new Date(dateInput);
    if (isNaN(d.getTime())) return String(dateInput);
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, "0");
    const minutes = String(d.getMinutes()).padStart(2, "0");
    if (includeSeconds) {
      const seconds = String(d.getSeconds()).padStart(2, "0");
      return `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;
    }
    return `${day}-${month}-${year} ${hours}:${minutes}`;
  } catch {
    return String(dateInput);
  }
}
