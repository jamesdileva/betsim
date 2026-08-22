import api from "./api";
import type { CalibrationReport, CalibrationRequest } from "../types/systemPlays";

export async function calibrate(request: CalibrationRequest): Promise<CalibrationReport> {
  const response = await api.post<CalibrationReport>("/api/system-plays", request);
  return response.data;
}
