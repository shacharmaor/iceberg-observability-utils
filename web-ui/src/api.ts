export type Severity = "warn" | "critical";

export interface Finding {
  signal: string;
  value: number;
  severity: Severity;
  threshold: number;
}

export interface TableOverview {
  namespace: string;
  table: string;
  findings: Finding[];
}

export async function fetchOverview(): Promise<TableOverview[]> {
  const response = await fetch("/api/overview");
  if (!response.ok) {
    throw new Error(`UI Backend answered ${response.status}`);
  }
  return (await response.json()).tables;
}
