import api from "../services/api";
import type { ModelPrediction } from "../types/ml";

export interface PredictRequest {
  source: "user_input" | "stub";
  win_probability?: number | null;
  confidence?: number | null;
  game_id?: string | null;
  odds_american?: number | null;
  model_id?: string | null;
}

export async function predict(request: PredictRequest): Promise<ModelPrediction> {
  const response = await api.post<ModelPrediction>("/api/models/predict", request);
  return response.data;
}
