import api from "./api";
import type { ParlayResponse } from "./apiTypes";

export interface ParlayLegInputApi {
  odds_american: number;
  win_probability: number;
}

export interface ParlayRequest {
  legs: ParlayLegInputApi[];
  bankroll: number;
  bet_size: number;
  bet_size_type: string;
  num_bets: number;
  num_simulations: number;
  seed?: number | null;
}

export type { ParlayResponse };

export async function simulateParlay(request: ParlayRequest): Promise<ParlayResponse> {
  const response = await api.post<ParlayResponse>("/api/parlay/simulate", request);
  return response.data;
}
