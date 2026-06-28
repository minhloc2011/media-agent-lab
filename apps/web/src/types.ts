export type JobStatus =
  | "uploaded"
  | "validating"
  | "converting"
  | "separating_stems"
  | "analyzing_mix"
  | "analyzing_vocal"
  | "detecting_language"
  | "generating_prompt"
  | "completed"
  | "failed_validation"
  | "failed_convert"
  | "failed_demucs"
  | "failed_mix_analysis"
  | "failed_vocal_analysis"
  | "failed_language_detection"
  | "failed_prompt_generation";

export interface JobCreateResponse {
  job_id: string;
  status: JobStatus;
}

export interface JobStatusResponse {
  id: string;
  status: JobStatus;
  progress: number;
  current_step: string;
  error_code: string | null;
  error_message: string | null;
}

export interface AnalysisResult {
  track: {
    bpm: number;
    tempo_bucket: string;
    key: string;
    scale: string;
    key_vi: string;
    energy: string;
    brightness: string;
    instrumentation: string[];
    confidence: Record<string, number>;
  };
  vocal: {
    median_pitch_hz: number;
    range_bucket: string;
    voice_descriptor: string;
    brightness: string;
    power: string;
    confidence: Record<string, number>;
  };
  language: {
    detected: string | null;
    label_vi: string | null;
    confidence: number;
    used_in_prompt: boolean;
  };
  prompt: {
    tags_vi: string;
    omitted_fields: string[];
    warnings: string[];
  };
}
