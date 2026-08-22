import { useEffect, useState } from "react";
import api, { type HealthResponse } from "./services/api";

type ConnectionStatus = "checking" | "connected" | "error";

export default function App() {
  const [status, setStatus] = useState<ConnectionStatus>("checking");
  const [detail, setDetail] = useState<string>("");

  useEffect(() => {
    api
      .get<HealthResponse>("/health")
      .then((res) => {
        setStatus("connected");
        setDetail(`Backend status: ${res.data.status}`);
      })
      .catch((err: unknown) => {
        setStatus("error");
        setDetail(err instanceof Error ? err.message : "Unknown error");
      });
  }, []);

  return (
    <main>
      <h1>Betsim</h1>
      <p data-testid="connection-status">
        {status === "checking" && "Checking backend connection..."}
        {status === "connected" && `Connected. ${detail}`}
        {status === "error" && `Backend unreachable. ${detail}`}
      </p>
    </main>
  );
}
