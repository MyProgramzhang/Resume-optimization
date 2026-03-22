<template>
  <section v-if="loading" class="card">
    <p class="eyebrow">加载中</p>
    <h2>正在获取优化结果</h2>
  </section>

  <section v-else-if="errorMessage" class="card">
    <p class="eyebrow">暂不可用</p>
    <h2>结果暂未就绪</h2>
    <p>{{ errorMessage }}</p>
  </section>

  <section v-else-if="result" class="stack-layout">
    <section class="card result-toolbar">
      <div>
        <p class="eyebrow">结果操作</p>
        <h2>优化结果已生成</h2>
        <p>下载的 PDF 会尽量沿用原始上传 PDF 的版式；下方双栏视图中，右侧仅对修改过的内容做红色加粗。</p>
      </div>
      <button class="primary-button" type="button" :disabled="downloading" @click="handleDownload">
        {{ downloading ? "准备下载中..." : "下载优化后 PDF" }}
      </button>
    </section>

    <ChangeSummary :items="result.change_summary" />
    <DiffSplitView :original-resume="result.parsed_resume" :optimized-resume="result.optimized_resume" />
  </section>
</template>

<script setup lang="ts">
import axios from "axios";
import { onMounted, ref } from "vue";

import ChangeSummary from "@/components/result/ChangeSummary.vue";
import DiffSplitView from "@/components/result/DiffSplitView.vue";
import { downloadOptimizedPdf, getJobResult } from "@/services/jobs";
import type { JobResultResponse } from "@/types/result";

const props = defineProps<{
  jobId: string;
}>();

const loading = ref(true);
const downloading = ref(false);
const errorMessage = ref("");
const result = ref<JobResultResponse | null>(null);

async function fetchResult() {
  loading.value = true;
  errorMessage.value = "";
  try {
    result.value = await getJobResult(props.jobId);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.detail || "获取结果失败。";
    } else {
      errorMessage.value = "获取结果失败。";
    }
  } finally {
    loading.value = false;
  }
}

async function handleDownload() {
  if (!result.value) {
    return;
  }

  downloading.value = true;
  try {
    const blob = await downloadOptimizedPdf(props.jobId);
    const fileName = `${stripPdfExtension(result.value.input.original_filename)}_优化版.pdf`;
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      window.alert(error.response?.data?.detail || "下载 PDF 失败。");
    } else {
      window.alert("下载 PDF 失败。");
    }
  } finally {
    downloading.value = false;
  }
}

function stripPdfExtension(filename: string): string {
  return filename.replace(/\.pdf$/i, "");
}

onMounted(fetchResult);
</script>
