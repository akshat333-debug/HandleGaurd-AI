import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Videos() {
  const [videos, setVideos] = useState([]);
  const [filename, setFilename] = useState("demo_shift.mp4");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function refresh() {
    setVideos(await api.videos());
  }

  useEffect(() => {
    refresh().catch((err) => setError(err.message));
  }, []);

  async function createAndProcess() {
    setBusy(true);
    setError("");
    try {
      const video = await api.createVideo(filename);
      const incidents = await api.processVideo(video.id);
      setMessage(`Processed ${video.id}: ${incidents.length} incident(s).`);
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4 max-w-3xl">
      <h1 className="text-2xl font-semibold">Video ingestion</h1>
      <p className="text-sm text-slate-500">
        Prototype processing uses the synthetic warehouse timeline so behaviours can be demonstrated without a GPU.
      </p>
      <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
        <label className="block text-sm">
          Filename
          <input
            className="mt-1 min-h-11 w-full rounded border border-slate-300 px-3"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
          />
        </label>
        <button
          disabled={busy}
          onClick={createAndProcess}
          className="min-h-11 cursor-pointer rounded bg-accent px-4 text-sm text-white disabled:opacity-50"
        >
          {busy ? "Processing…" : "Create + process demo video"}
        </button>
        {message && <p className="text-sm text-slate-600">{message}</p>}
        {error && (
          <p className="text-sm text-red-700" role="alert">
            {error}
          </p>
        )}
      </div>
      <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
        {videos.map((video) => (
          <li key={video.id} className="px-4 py-3 text-sm flex justify-between">
            <span className="font-mono">{video.id}</span>
            <span>
              {video.filename} · {video.status} · {video.loading_bay}
            </span>
          </li>
        ))}
        {videos.length === 0 && <li className="px-4 py-3 text-sm text-slate-500">No videos yet.</li>}
      </ul>
    </div>
  );
}
