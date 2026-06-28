import type { AnalysisResult, JobCreateResponse, JobStatusResponse } from "./types";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function createJob(file: File): Promise<JobCreateResponse> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch("/api/jobs", {
    method: "POST",
    body: form
  });
  return parseJson<JobCreateResponse>(response);
}

export async function getJob(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`/api/jobs/${jobId}`);
  return parseJson<JobStatusResponse>(response);
}

export async function getResult(jobId: string): Promise<AnalysisResult> {
  const response = await fetch(`/api/jobs/${jobId}/result`);
  return parseJson<AnalysisResult>(response);
}
