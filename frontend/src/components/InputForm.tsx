import { useState } from "react";

interface Props {
  onSubmit: (value: string) => Promise<void>;
  isLoading: boolean;
}

export default function InputForm({ onSubmit, isLoading }: Props) {
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim()) {
      setError("Enter a research plan or DOI/link.");
      return;
    }
    setError(null);
    await onSubmit(value.trim());
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="glass p-6 rounded-xl space-y-4 shadow-lg"
    >
      <div>
        <label className="text-sm uppercase tracking-wide text-slate-300">
          Research plan or paper link / DOI
        </label>
        <textarea
          className="w-full mt-2 rounded-lg border border-slate-700 bg-slate-900/60 p-3 focus:border-accent focus:outline-none"
          rows={4}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Describe your research idea or paste a DOI / paper URL"
        />
      </div>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-lg bg-gradient-to-r from-accent to-teal text-black font-semibold py-3 hover:opacity-90 transition disabled:opacity-50"
      >
        {isLoading ? "Generating..." : "Generate Research Web"}
      </button>
    </form>
  );
}
