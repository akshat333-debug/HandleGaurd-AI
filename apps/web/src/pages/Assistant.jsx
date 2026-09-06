import { useState } from "react";
import { api } from "../api.js";

const SUGGESTIONS = [
  "Show high-risk events from today",
  "Show drop incidents",
  "Which bay had the highest event count?",
  "How many false positives occurred?",
];

export default function Assistant() {
  const [question, setQuestion] = useState(SUGGESTIONS[0]);
  const [reply, setReply] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function ask(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      setReply(await api.assistant(question));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-2xl space-y-4">
      <h1 className="text-2xl font-semibold">Supervisor assistant</h1>
      <p className="text-sm text-slate-500">
        Answers are grounded in stored incidents and SOP rules. The assistant will not identify workers or claim confirmed damage.
      </p>
      <form onSubmit={ask} className="space-y-3">
        <label className="block text-sm">
          Question
          <textarea
            className="mt-1 w-full min-h-24 rounded border border-slate-300 p-2"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </label>
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((item) => (
            <button
              type="button"
              key={item}
              onClick={() => setQuestion(item)}
              className="min-h-11 cursor-pointer rounded border border-slate-300 px-3 text-xs"
            >
              {item}
            </button>
          ))}
        </div>
        <button
          disabled={busy}
          className="min-h-11 cursor-pointer rounded bg-slate-800 px-4 text-sm text-white disabled:opacity-50"
        >
          {busy ? "Querying…" : "Ask"}
        </button>
      </form>
      {error && (
        <p className="text-sm text-red-700" role="alert">
          {error}
        </p>
      )}
      {reply && (
        <section className="rounded-lg border border-slate-200 bg-white p-4 space-y-2">
          {reply.blocked && (
            <p className="text-xs uppercase tracking-wide text-accent">Guardrail blocked</p>
          )}
          <p className="text-sm leading-relaxed">{reply.answer}</p>
          {reply.citations.length > 0 && (
            <p className="font-mono text-xs text-slate-500">Citations: {reply.citations.join(", ")}</p>
          )}
        </section>
      )}
    </div>
  );
}
