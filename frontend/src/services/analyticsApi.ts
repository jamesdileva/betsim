import api from "./api";
import type { PerformanceResponse, RunBacktestsResponse } from "../types/analytics";

export async function getPerformance(modelId?: string): Promise<PerformanceResponse> {
  const response = await api.get<PerformanceResponse>("/api/analytics/performance", {
    params: modelId ? { model_id: modelId } : {},
  });
  return response.data;
}

export async function runBacktests(modelId?: string): Promise<RunBacktestsResponse> {
  const response = await api.post<RunBacktestsResponse>(
    "/api/analytics/run-backtests",
    null,
    { params: modelId ? { model_id: modelId } : {} },
  );
  return response.data;
}
