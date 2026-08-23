import api from "./api";
import type { Portfolio } from "../types/portfolio";

export async function buildPortfolio(bankroll: number, modelId?: string): Promise<Portfolio> {
  const response = await api.post<Portfolio>("/api/portfolio/build", null, {
    params: { bankroll, ...(modelId ? { model_id: modelId } : {}) },
  });
  return response.data;
}

export async function getLatestPortfolio(): Promise<Portfolio | null> {
  const response = await api.get<Portfolio | null>("/api/portfolio/latest");
  return response.data;
}
