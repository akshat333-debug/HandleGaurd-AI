import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";

export default function Incidents() {
  const [rows, setRows] = useState([]);
  const [behaviour, setBehaviour] = useState("");
  const [risk, setRisk] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .incidents({ behaviour, risk_level: risk, status })
      .then(setRows)
      .catch((err) => setError(err.message));
  }, [behaviour, risk, status]);

  const behaviours = useMemo(() => [...new Set(rows.map((r) => r.behaviour))], [rows]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Incidents</h1>
      {error && (
        <p className="text-sm text-red-700" role="alert">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-3">
        <label className="text-sm">
          Behaviour
          <select
            className="ml-2 min-h-11 rounded border border-slate-300 bg-white px-2"
            value={behaviour}
            onChange={(e) => setBehaviour(e.target.value)}
          >
            <option value="">All</option>
            {behaviours.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Risk
          <select
            className="ml-2 min-h-11 rounded border border-slate-300 bg-white px-2"
            value={risk}
            onChange={(e) => setRisk(e.target.value)}
          >
            <option value="">All</option>
            {["Critical", "High", "Medium", "Low"].map((l) => (
              <option key={l}>{l}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Status
          <select
            className="ml-2 min-h-11 rounded border border-slate-300 bg-white px-2"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">All</option>
            {["NEW", "CONFIRMED", "FALSE_POSITIVE", "RESOLVED"].map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </label>
      </div>
      <div className="rounded-lg border border-slate-200 bg-white overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-2">ID</th>
              <th className="px-4 py-2">Behaviour</th>
              <th className="px-4 py-2">Bay</th>
              <th className="px-4 py-2">Risk</th>
              <th className="px-4 py-2">Confidence</th>
              <th className="px-4 py-2">t0-t1</th>
              <th className="px-4 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((item) => (
              <tr key={item.id} className="border-t border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-2 font-mono">
                  <Link className="text-accent cursor-pointer" to={`/incidents/${item.id}`}>
                    {item.id}
                  </Link>
                </td>
                <td className="px-4 py-2">{item.behaviour.replaceAll("_", " ")}</td>
                <td className="px-4 py-2">{item.loading_bay || "—"}</td>
                <td className="px-4 py-2 font-mono">
                  {item.risk_score.toFixed(0)} {item.risk_level}
                </td>
                <td className="px-4 py-2 font-mono">{item.confidence.toFixed(2)}</td>
                <td className="px-4 py-2 font-mono">
                  {item.start_time.toFixed(1)}–{item.end_time.toFixed(1)}s
                </td>
                <td className="px-4 py-2">{item.review_status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <p className="p-4 text-sm text-slate-500">No matching incidents.</p>}
      </div>
    </div>
  );
}
