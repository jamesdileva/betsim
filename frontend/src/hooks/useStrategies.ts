import { useCallback, useEffect, useState } from "react";
import {
  createStrategy,
  deleteStrategy,
  listStrategies,
  updateStrategy,
} from "../services/strategiesApi";
import type { Strategy, StrategyCreateInput } from "../types/strategy";

export function useStrategies() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setStrategies(await listStrategies());
    } catch {
      setError("Could not load strategies. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const save = useCallback(async (input: StrategyCreateInput) => {
    const created = await createStrategy(input);
    setStrategies((prev) => [created, ...prev]);
    return created;
  }, []);

  const edit = useCallback(
    async (id: number, patch: Partial<StrategyCreateInput>) => {
      const updated = await updateStrategy(id, patch);
      setStrategies((prev) => prev.map((s) => (s.id === id ? updated : s)));
      return updated;
    },
    [],
  );

  const remove = useCallback(async (id: number) => {
    await deleteStrategy(id);
    setStrategies((prev) => prev.filter((s) => s.id !== id));
  }, []);

  return { strategies, loading, error, refresh, save, edit, remove };
}
