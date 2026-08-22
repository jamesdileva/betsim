export default function PlaceholderPage({ title, sprint }: { title: string; sprint: string }) {
  return (
    <div className="p-6">
      <h1 className="mb-2 text-lg font-bold">{title}</h1>
      <p className="text-text-muted">This page arrives in Sprint {sprint}.</p>
    </div>
  );
}
