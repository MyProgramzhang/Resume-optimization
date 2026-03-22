<template>
  <section class="page-grid">
    <div class="hero-copy">
      <p class="eyebrow">上传简历 → 智能优化 → 对比结果</p>
      <h2>将原始 PDF 简历优化成更强的版本，并清楚展示每一处修改。</h2>
      <p>
        这个本地网页应用会在你的电脑上完成上传、处理和展示流程，智能优化步骤则可以调用云端大模型接口。
      </p>
    </div>
    <ResumeUploadForm :submitting="submitting" @submit="handleSubmit" />
  </section>
</template>

<script setup lang="ts">
import axios from "axios";
import { ref } from "vue";
import { useRouter } from "vue-router";

import ResumeUploadForm from "@/components/upload/ResumeUploadForm.vue";
import { createJob } from "@/services/jobs";
import type { CreateJobInput } from "@/types/job";

const router = useRouter();
const submitting = ref(false);

async function handleSubmit(payload: CreateJobInput) {
  submitting.value = true;
  try {
    const response = await createJob(payload);
    router.push({ name: "job", params: { jobId: response.job_id } });
  } catch (error) {
    if (axios.isAxiosError(error)) {
      window.alert(error.response?.data?.detail || "提交任务失败。");
    } else {
      window.alert("提交任务失败。");
    }
  } finally {
    submitting.value = false;
  }
}
</script>
