import type { ColumnClassification } from "@/types/classification.types";

/**
 * Centralized privacy protection helper.
 * If a column is classified with expose_values === false, sample data and
 * profiling top_values must be masked on the client.
 */
export function isColumnExposeSuppressed(
  columnName: string,
  classifications?: ColumnClassification[]
): boolean {
  if (!classifications || classifications.length === 0) return false;
  const match = classifications.find(
    (c) =>
      (c.name || c.column_name || "").toLowerCase() === columnName.toLowerCase()
  );
  return match ? match.expose_values === false : false;
}

/**
 * Get sensitivity level of a column from classification metadata.
 */
export function getColumnSensitivity(
  columnName: string,
  classifications?: ColumnClassification[]
): string | undefined {
  if (!classifications || classifications.length === 0) return undefined;
  const match = classifications.find(
    (c) =>
      (c.name || c.column_name || "").toLowerCase() === columnName.toLowerCase()
  );
  return match?.sensitivity;
}
