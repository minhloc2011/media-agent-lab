import { Clipboard, Download, FileAudio, Loader2, Upload } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { createJob, getJob, getResult } from "./api";
import type { AnalysisResult, JobStatusResponse } from "./types";

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<JobStatusResponse | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const canUpload = useMemo(() => file !== null && !isUploading, [file, isUploading]);

  useEffect(() => {
    if (!jobId || job?.status === "completed") {
      return;
    }

    const timer = window.setInterval(async () => {
      const nextJob = await getJob(jobId);
      setJob(nextJob);
      if (nextJob.status === "completed") {
        setResult(await getResult(jobId));
      }
    }, 1000);

    return () => window.clearInterval(timer);
  }, [jobId, job?.status]);

  async function handleUpload() {
    if (!file) {
      return;
    }

    setError(null);
    setIsUploading(true);
    try {
      const created = await createJob(file);
      setJobId(created.job_id);
      const current = await getJob(created.job_id);
      setJob(current);
      if (current.status === "completed") {
        setResult(await getResult(created.job_id));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  async function copyPrompt() {
    if (result) {
      await navigator.clipboard.writeText(result.prompt.tags_vi);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-5 py-8">
        <header className="flex items-center justify-between border-b border-neutral-800 pb-5">
          <div>
            <h1 className="text-2xl font-semibold">Media Agent Lab</h1>
            <p className="mt-1 text-sm text-neutral-400">MP3 reference to Vietnamese ACE-Step prompt</p>
          </div>
          <div className="rounded bg-emerald-500/15 px-3 py-1 text-sm text-emerald-300">CUDA-ready MVP</div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
          <div className="rounded border border-neutral-800 bg-neutral-900 p-5">
            <div className="flex items-center gap-3">
              <FileAudio className="h-5 w-5 text-cyan-300" />
              <h2 className="text-lg font-medium">Upload MP3</h2>
            </div>
            <label className="mt-5 flex min-h-48 cursor-pointer flex-col items-center justify-center rounded border border-dashed border-neutral-700 bg-neutral-950 px-4 text-center hover:border-cyan-400">
              <Upload className="mb-3 h-8 w-8 text-neutral-500" />
              <span className="text-sm text-neutral-300">{file ? file.name : "Choose one .mp3 file"}</span>
              <input
                className="hidden"
                type="file"
                accept=".mp3,audio/mpeg"
                onChange={(event: { target: { files: FileList | null } }) => setFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <button
              className="mt-4 flex w-full items-center justify-center gap-2 rounded bg-cyan-400 px-4 py-2 font-medium text-neutral-950 disabled:cursor-not-allowed disabled:bg-neutral-700 disabled:text-neutral-400"
              disabled={!canUpload}
              onClick={handleUpload}
            >
              {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
              Analyze
            </button>
            {error && <p className="mt-3 text-sm text-red-300">{error}</p>}
          </div>

          <div className="rounded border border-neutral-800 bg-neutral-900 p-5">
            <h2 className="text-lg font-medium">Job Status</h2>
            {job ? (
              <div className="mt-5">
                <div className="flex items-center justify-between text-sm text-neutral-300">
                  <span>{job.current_step}</span>
                  <span>{job.progress}%</span>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded bg-neutral-800">
                  <div className="h-full bg-cyan-400" style={{ width: `${job.progress}%` }} />
                </div>
                <p className="mt-3 text-xs text-neutral-500">{job.id}</p>
              </div>
            ) : (
              <p className="mt-5 text-sm text-neutral-400">Upload a file to create a local analysis job.</p>
            )}
          </div>
        </section>

        {result && (
          <section className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
            <div className="rounded border border-neutral-800 bg-neutral-900 p-5">
              <div className="flex items-center justify-between gap-4">
                <h2 className="text-lg font-medium">ACE-Step Prompt</h2>
                <button className="rounded bg-neutral-100 px-3 py-2 text-sm font-medium text-neutral-950" onClick={copyPrompt}>
                  <Clipboard className="mr-2 inline h-4 w-4" />
                  Copy
                </button>
              </div>
              <p className="mt-5 text-xl leading-relaxed text-neutral-100">{result.prompt.tags_vi}</p>
              <a
                className="mt-5 inline-flex items-center gap-2 text-sm text-cyan-300"
                href={`/api/jobs/${jobId}/assets/metadata`}
              >
                <Download className="h-4 w-4" />
                Download metadata JSON
              </a>
            </div>

            <div className="rounded border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-lg font-medium">Metadata</h2>
              <dl className="mt-5 grid grid-cols-2 gap-3 text-sm">
                <dt className="text-neutral-500">Tempo</dt>
                <dd>{result.track.bpm} BPM</dd>
                <dt className="text-neutral-500">Key</dt>
                <dd>{result.track.key_vi}</dd>
                <dt className="text-neutral-500">Voice</dt>
                <dd>{result.vocal.voice_descriptor}</dd>
                <dt className="text-neutral-500">Brightness</dt>
                <dd>{result.track.brightness}</dd>
              </dl>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
