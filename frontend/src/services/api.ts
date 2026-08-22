import axios from "axios";

export interface HealthResponse {
  status: string;
}

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 5000,
});

export default api;
