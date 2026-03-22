import api from "./api";
import type { CreateJobInput, CreateJobResponse, JobStatusResponse } from "@/types/job";
import type { JobResultResponse } from "@/types/result";

export async function createJob(input: CreateJobInput): Promise<CreateJobResponse> {
  const formData = new FormData();
  formData.append("resume_file", input.resume_file);
  formData.append("mode", input.mode);
  formData.append("job_description", input.job_description || "");
  formData.append("target_role", input.target_role || "");
  formData.append("notes", input.notes || "");
  const response = await api.post<CreateJobResponse>("/api/jobs", formData);
  return response.data;
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await api.get<JobStatusResponse>(`/api/jobs/${jobId}`);
  return response.data;
}

export async function getJobResult(jobId: string): Promise<JobResultResponse> {
  const response = await api.get<JobResultResponse>(`/api/jobs/${jobId}/result`);
  return response.data;
}

export async function downloadOptimizedPdf(jobId: string): Promise<Blob> {
  const response = await api.get<Blob>(`/api/jobs/${jobId}/optimized-pdf`, {
    responseType: "blob",
  });
  return response.data;
}
