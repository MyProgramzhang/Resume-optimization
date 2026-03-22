export type JobMode = "general" | "jd_targeted";
export type JobStatus = "queued" | "parsing" | "structuring" | "optimizing" | "diffing" | "completed" | "failed";

export type CreateJobResponse = {
  job_id: string;
  status: JobStatus;
  current_step: string;
  progress: number;
  created_at: string;
};

export type JobStatusResponse = {
  job_id: string;
  status: JobStatus;
  current_step: string;
  progress: number;
  error_message: string | null;
  warnings: string[];
  created_at: string;
  updated_at: string;
};

export type CreateJobInput = {
  resume_file: File;
  mode: JobMode;
  job_description?: string;
  target_role?: string;
  notes?: string;
};
