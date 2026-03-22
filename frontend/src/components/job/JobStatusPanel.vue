<template>
  <section class="card">
    <div class="status-head">
      <div>
        <p class="eyebrow">任务状态</p>
        <h2>{{ statusLabel }}</h2>
      </div>
      <span class="status-pill" :class="status.status">{{ localizedStatus }}</span>
    </div>

    <ProgressBar :value="status.progress" />

    <dl class="status-grid">
      <div>
        <dt>当前步骤</dt>
        <dd>{{ localizedStep }}</dd>
      </div>
      <div>
        <dt>进度</dt>
        <dd>{{ status.progress }}%</dd>
      </div>
    </dl>

    <div v-if="status.warnings.length" class="warning-box">
      <p v-for="warning in status.warnings" :key="warning">{{ warning }}</p>
    </div>

    <p v-if="status.error_message" class="error-text">{{ status.error_message }}</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { JobStatusResponse } from "@/types/job";
import ProgressBar from "./ProgressBar.vue";

const props = defineProps<{
  status: JobStatusResponse;
}>();

const statusLabel = computed(() => {
  if (props.status.status === "completed") return "简历优化已完成";
  if (props.status.status === "failed") return "本次任务需要处理";
  return "简历优化智能体正在处理中";
});

const statusTextMap: Record<JobStatusResponse["status"], string> = {
  queued: "排队中",
  parsing: "解析中",
  structuring: "结构化处理中",
  optimizing: "优化中",
  diffing: "生成对比中",
  completed: "已完成",
  failed: "失败",
};

const stepTextMap: Record<string, string> = {
  uploaded: "文件已上传",
  extracting_pdf_text: "正在提取 PDF 文本",
  structuring_resume: "正在整理简历结构",
  optimizing_resume: "正在优化简历内容",
  building_diff: "正在生成新旧对比",
  finished: "处理完成",
  failed: "处理失败",
};

const localizedStatus = computed(() => statusTextMap[props.status.status] || props.status.status);
const localizedStep = computed(() => stepTextMap[props.status.current_step] || props.status.current_step);
</script>
