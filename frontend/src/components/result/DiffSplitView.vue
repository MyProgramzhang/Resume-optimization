<template>
  <section class="diff-resume-grid">
    <ResumePreview title="原简历" :resume="originalResume" />
    <ResumePreview title="修改后简历" :resume="optimizedResume" :compare-resume="originalResume" :highlight-changes="true" />
  </section>
</template>

<script setup lang="ts">
import type { JobResultResponse } from "@/types/result";
import ResumePreview from "./ResumePreview.vue";

defineProps<{
  originalResume: JobResultResponse["parsed_resume"];
  optimizedResume: JobResultResponse["optimized_resume"];
}>();
</script>
