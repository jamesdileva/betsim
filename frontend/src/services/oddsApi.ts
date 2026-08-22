import api from "./api";
import type { GamesResponse } from "../types/odds";

export async function listGames(sport: string): Promise<GamesResponse> {
  const response = await api.get<GamesResponse>("/api/odds/games", {
    params: { sport },
  });
  return response.data;
}
