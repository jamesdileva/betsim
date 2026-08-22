import type { SimulationResult } from "../types/simulation";

function csvEscape(value: string | number): string {
  const s = String(value);
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

/**
 * Build a CSV string from a simulation result: a metrics section followed by
 * the distribution histogram.
 */
export function resultToCsv(result: SimulationResult): string {
  const lines: string[] = [];

  lines.push("metric,value");
  const metrics: [string, number][] = [
    ["win_pct", result.metrics.win_pct],
    ["avg_ending_bankroll", result.metrics.avg_ending_bankroll],
    ["median_ending_bankroll", result.metrics.median_ending_bankroll],
    ["std_dev", result.metrics.std_dev],
    ["min_bankroll", result.metrics.min_bankroll],
    ["max_bankroll", result.metrics.max_bankroll],
    ["risk_of_ruin", result.metrics.risk_of_ruin],
    ["avg_max_drawdown", result.metrics.avg_max_drawdown],
    ["worst_case_drawdown", result.metrics.worst_case_drawdown],
    ["ev_per_bet", result.metrics.ev_per_bet],
    ["ev_total", result.metrics.ev_total],
  ];
  for (const [name, value] of metrics) {
    lines.push(`${csvEscape(name)},${value}`);
  }

  lines.push("");
  lines.push("bin_low,bin_high,count");
  const { bin_edges, counts } = result.distribution;
  counts.forEach((count, i) => {
    lines.push([bin_edges[i], bin_edges[i + 1], count].map(csvEscape).join(","));
  });

  return lines.join("\n");
}

export function downloadCsv(filename: string, csv: string): void {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}
