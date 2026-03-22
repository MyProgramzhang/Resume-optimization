<template>
  <section class="stack-layout">
    <JobStatusPanel v-if="status" :status="status" />
    <section v-if="status?.status !== 'failed'" class="card subtle-card">
      <p class="eyebrow">实时处理中</p>
      <h2>系统正在提取、整理并优化你的简历内容。</h2>
      <p>任务完成后，页面会自动跳转到结果页。</p>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import JobStatusPanel from "@/components/job/JobStatusPanel.vue";
import { getJobStatus } from "@/services/jobs";
import type { JobStatusResponse } from "@/types/job";

const props = defineProps<{
  jobId: string;
}>();

const router = useRouter();
const status = ref<JobStatusResponse | null>(null);
let timer: number | undefined;

async function fetchStatus() {
  const next = await getJobStatus(props.jobId);
  status.value = next;
  if (next.status === "completed") {
    stopPolling();
    router.replace({ name: "result", params: { jobId: props.jobId } });
  }
  if (next.status === "failed") {
    stopPolling();
  }
}

function startPolling() {
  fetchStatus();
  timer = window.setInterval(fetchStatus, 2000);
}

function stopPolling() {
  if (timer) {
    window.clearInterval(timer);
    timer = undefined;
  }
}

onMounted(startPolling);
onBeforeUnmount(stopPolling);
</script>
