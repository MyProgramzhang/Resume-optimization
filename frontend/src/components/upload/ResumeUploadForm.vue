<template>
  <form class="card upload-card" @submit.prevent="submitForm">
    <div class="field-group">
      <label class="field-label" for="resumeFile">简历 PDF</label>
      <input id="resumeFile" type="file" accept="application/pdf" @change="onFileChange" />
      <p class="helper-text">V1 仅支持可提取文本的 PDF 简历。</p>
    </div>

    <ModeSelector v-model="mode" />

    <div class="field-grid">
      <div class="field-group">
        <label class="field-label" for="targetRole">目标岗位</label>
        <input id="targetRole" v-model="targetRole" type="text" placeholder="如：产品经理" />
      </div>
      <div class="field-group">
        <label class="field-label" for="notes">补充说明</label>
        <input id="notes" v-model="notes" type="text" placeholder="可选：语气、重点方向等要求" />
      </div>
    </div>

    <JobDescriptionInput v-if="mode === 'jd_targeted'" v-model="jobDescription" />

    <p v-if="error" class="error-text">{{ error }}</p>

    <button class="primary-button" type="submit" :disabled="submitting">
      {{ submitting ? "提交中..." : "开始优化简历" }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref } from "vue";

import type { CreateJobInput, JobMode } from "@/types/job";
import JobDescriptionInput from "./JobDescriptionInput.vue";
import ModeSelector from "./ModeSelector.vue";

const emit = defineEmits<{
  submit: [payload: CreateJobInput];
}>();

defineProps<{
  submitting: boolean;
}>();

const selectedFile = ref<File | null>(null);
const mode = ref<JobMode>("general");
const jobDescription = ref("");
const targetRole = ref("");
const notes = ref("");
const error = ref("");

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  selectedFile.value = input.files?.[0] || null;
}

function submitForm() {
  if (!selectedFile.value) {
    error.value = "请先上传 PDF 简历。";
    return;
  }
  if (!selectedFile.value.name.toLowerCase().endsWith(".pdf")) {
    error.value = "仅支持 PDF 文件。";
    return;
  }
  if (mode.value === "jd_targeted" && !jobDescription.value.trim()) {
    error.value = "岗位定制模式下请先填写职位描述。";
    return;
  }
  error.value = "";
  emit("submit", {
    resume_file: selectedFile.value,
    mode: mode.value,
    job_description: jobDescription.value,
    target_role: targetRole.value,
    notes: notes.value,
  });
}
</script>
