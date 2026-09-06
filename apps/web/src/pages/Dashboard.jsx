import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api.js";

const LEVELS = ["Critical", "High", "Medium", "Low"];
const LEVEL_COLOR = {
  Critical: "bg-red-600",
  High: "bg-orange-500",
  Medium: "bg-amber-400",
  Low: "bg-slate-400",
};

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.summary(), api.incidents()])
      .then(([s, i]) => {
        setSummary(s);
        setIncidents(i.slice(0, 8));
      })
      .catch((err) => setError(err.message));
  }, []);

  const chartData = Object.entries(summary?.by_behaviour || {}).map(([name, count]) => ({
    name: name.replaceAll("_", " "),
    count,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Today's risk events</h1>
        <p className="text-sm text-slate-500">Observed handling risk — not confirmed product damage.</p>
      </div>
      {error && (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
          {error} Start the API with uvicorn if this is a network error.
        </p>
      )}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {LEVELS.map((level) => (
          <article key={level} className="rounded-lg border border-slate-200 bg-white p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">{level}</p>
            <p className="mt-2 font-mono text-3xl">{summary?.by_level?.[level] ?? 0}</p>
            <span className={`mt-3 inline-block h-1.5 w-12 rounded ${LEVEL_COLOR[level]}`} />
          </article>
        ))}
      </section>
      <section className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-medium mb-3">Behaviour distribution</h2>
          {chartData.length === 0 ? (
            <p className="text-sm text-slate-500">No incidents yet. Process a demo video to populate this chart.</p>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={70} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#EA580C" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-medium mb-3">Loading bays</h2>
          <ul className="space-y-2 text-sm">
            {Object.entries(summary?.by_bay || {}).map(([bay, count]) => (
              <li key={bay} className="flex justify-between">
                <span>{bay}</span>
                <span className="font-mono">{count}</span>
              </li>
            ))}
            {!summary?.by_bay && <li className="text-slate-500">No bay data</li>}
          </ul>
        </div>
      </section>
      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
          <h2 className="text-sm font-medium">Recent incidents</h2>
          <Link to="/incidents" className="text-sm text-accent cursor-pointer">
            View all
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-2">ID</th>
                <th className="px-4 py-2">Behaviour</th>
                <th className="px-4 py-2">Risk</th>
                <th className="px-4 py-2">Confidence</th>
                <th className="px-4 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((item) => (
                <tr key={item.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-2 font-mono">
                    <Link to={`/incidents/${item.id}`} className="text-accent cursor-pointer">
                      {item.id}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{item.behaviour.replaceAll("_", " ")}</td>
                  <td className="px-4 py-2 font-mono">
                    {item.risk_score.toFixed(0)} / {item.risk_level}
                  </td>
                  <td className="px-4 py-2 font-mono">{item.confidence.toFixed(2)}</td>
                  <td className="px-4 py-2">{item.review_status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
