import type { ResumeSchema } from "./resume";

export type DiffBlock = {
  section: "summary" | "experience" | "education" | "projects" | "skills";
  block_id: string;
  old_text: string;
  new_text: string;
  change_type: string;
  reason: string;
};

export type JobResultResponse = {
  job_id: string;
  input: {
    mode: string;
    target_role: string;
    original_filename: string;
  };
  parsed_resume: ResumeSchema;
  optimized_resume: ResumeSchema;
  change_summary: string[];
  diff_blocks: DiffBlock[];
  meta: {
    processing_ms: number;
    parser_warning: string | null;
    model_name: string;
  };
};
