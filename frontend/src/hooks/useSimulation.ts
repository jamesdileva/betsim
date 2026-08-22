import api from "../services/api";
import type { SimulationParams, SimulationResult } from "../types/simulation";
import { useCallback, useState } from "react";

type SimulationStatus = "idle" | "loading" | "success" | "error";

export function useSimulation() {
  const [status, setStatus] = useState<SimulationStatus>("idle");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runSimulation = useCallback(async (params: SimulationParams) => {
    setStatus("loading");
    setError(null);
    try {
      const response = await api.post<SimulationResult>("/api/simulate", params);
      setResult(response.data);
      setStatus("success");
    } catch (err: unknown) {
      let message = "Something went wrong running the simulation.";
      if (typeof err === "object" && err !== null && "response" in err) {
        const axiosError = err as { response?: { data?: { detail?: unknown } } };
        const detail = axiosError.response?.data?.detail;
        if (typeof detail === "string") {
          message = detail;
        } else if (Array.isArray(detail)) {
          message = detail
            .map((d) => (typeof d === "object" && d !== null && "msg" in d ? String((d as { msg: unknown }).msg) : ""))
            .filter(Boolean)
            .join("; ");
        }
      }
      setError(message);
      setStatus("error");
    }
  }, []);

  return { status, result, error, runSimulation };
}
