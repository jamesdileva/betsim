import api from "./api";
import type { RunSummary } from "../types/strategy";
import type { Strategy, StrategyCreateInput } from "../types/strategy";

export async function listStrategies(): Promise<Strategy[]> {
  const response = await api.get<Strategy[]>("/api/strategies");
  return response.data;
}

export async function createStrategy(input: StrategyCreateInput): Promise<Strategy> {
  const response = await api.post<Strategy>("/api/strategies", input);
  return response.data;
}

export async function updateStrategy(
  id: number,
  patch: Partial<StrategyCreateInput>,
): Promise<Strategy> {
  const response = await api.put<Strategy>(`/api/strategies/${id}`, patch);
  return response.data;
}

export async function deleteStrategy(id: number): Promise<void> {
  await api.delete(`/api/strategies/${id}`);
}

export async function listRuns(limit = 50): Promise<RunSummary[]> {
  const response = await api.get<{ runs: RunSummary[] }>(`/api/runs?limit=${limit}`);
  return response.data.runs;
}

export async function deleteRun(runId: number): Promise<void> {
  await api.delete(`/api/runs/${runId}`);
}
