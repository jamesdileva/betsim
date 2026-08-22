interface LiveOddsBadgeProps {
  /** true = older than the 2h threshold, false = fresh, null = never fetched */
  stale: boolean | null;
}

export default function LiveOddsBadge({ stale }: LiveOddsBadgeProps) {
  return (
    <span
      data-testid="odds-badge"
      className={`text-xs font-semibold ${
        stale === null ? "text-text-muted" : stale ? "text-warning" : "text-success"
      }`}
    >
      {stale === null ? "No odds fetched" : stale ? "Stale" : "Live"}
    </span>
  );
}
