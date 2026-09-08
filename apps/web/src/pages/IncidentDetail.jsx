import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";

export default function IncidentDetail() {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .incident(id)
      .then((data) => {
        setItem(data);
        setNote(data.supervisor_note || "");
      })
      .catch((err) => setError(err.message));
  }, [id]);

  async function downloadReport(fmt) {
    setBusy(true);
    try {
      const report = await api.incidentReport(id, fmt);
      const blob = new Blob(
        [fmt === "markdown" ? report.markdown : JSON.stringify(report, null, 2)],
        { type: fmt === "markdown" ? "text/markdown" : "application/json" }
      );
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${id}.${fmt === "markdown" ? "md" : "json"}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function review(review_status) {
    setBusy(true);
    try {
      const updated = await api.patchIncident(id, { review_status, supervisor_note: note });
      setItem(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (!item) {
    return <p className="text-sm text-slate-500">{error || "Loading incident…"}</p>;
  }

  return (
    <div className="space-y-4 max-w-3xl">
      <Link to="/incidents" className="text-sm text-accent cursor-pointer">
        Back to incidents
      </Link>
      <h1 className="font-mono text-2xl">{item.id}</h1>
      <p className="text-slate-500">
        {item.behaviour.replaceAll("_", " ")} · {item.loading_bay} · {item.zone || "no zone"}
      </p>
      <div className="grid grid-cols-2 gap-3">
        <article className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-xs uppercase text-slate-500">Risk</p>
          <p className="font-mono text-3xl">
            {item.risk_score.toFixed(0)}
            <span className="text-base text-slate-500"> / 100 {item.risk_level}</span>
          </p>
        </article>
        <article className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-xs uppercase text-slate-500">Confidence</p>
          <p className="font-mono text-3xl">{item.confidence.toFixed(2)}</p>
        </article>
      </div>
      <section className="rounded-lg border border-slate-200 bg-white p-4 space-y-2">
        <h2 className="text-sm font-medium">Explanation</h2>
        <p className="text-sm leading-relaxed">{item.explanation}</p>
        <h2 className="text-sm font-medium pt-2">Recommended action</h2>
        <p className="text-sm leading-relaxed">{item.recommendation}</p>
        <h2 className="text-sm font-medium pt-2">Evidence</h2>
        <pre className="text-xs bg-muted rounded p-3 overflow-x-auto font-mono">
          {JSON.stringify(item.evidence, null, 2)}
        </pre>
      </section>
      <section className="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
        <label className="block text-sm">
          Supervisor note
          <textarea
            className="mt-1 w-full min-h-24 rounded border border-slate-300 p-2"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
        </label>
        <div className="flex flex-wrap gap-2">
          <button
            disabled={busy}
            onClick={() => review("CONFIRMED")}
            className="min-h-11 cursor-pointer rounded bg-slate-800 px-4 text-sm text-white disabled:opacity-50"
          >
            Confirm incident
          </button>
          <button
            disabled={busy}
            onClick={() => review("FALSE_POSITIVE")}
            className="min-h-11 cursor-pointer rounded border border-slate-300 px-4 text-sm"
          >
            Mark false positive
          </button>
          <button
            disabled={busy}
            onClick={() => review("RESOLVED")}
            className="min-h-11 cursor-pointer rounded border border-slate-300 px-4 text-sm"
          >
            Resolve
          </button>
          <button
            disabled={busy}
            onClick={() => downloadReport("json")}
            className="min-h-11 cursor-pointer rounded border border-slate-300 px-4 text-sm"
          >
            Export JSON
          </button>
          <button
            disabled={busy}
            onClick={() => downloadReport("markdown")}
            className="min-h-11 cursor-pointer rounded border border-slate-300 px-4 text-sm"
          >
            Export Markdown
          </button>
        </div>
        {error && (
          <p className="text-sm text-red-700" role="alert">
            {error}
          </p>
        )}
      </section>
    </div>
  );
}
