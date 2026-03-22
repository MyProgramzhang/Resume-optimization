<template>
  <article class="diff-card">
    <div class="diff-card-header">
      <div>
        <p class="eyebrow">{{ sectionLabel }}</p>
        <h3>{{ block.block_id }}</h3>
      </div>
      <span class="diff-type">{{ changeTypeLabel }}</span>
    </div>
    <div class="diff-columns">
      <div>
        <h4>修改前</h4>
        <pre>{{ block.old_text || "暂无内容" }}</pre>
      </div>
      <div>
        <h4>修改后</h4>
        <pre>{{ block.new_text || "暂无内容" }}</pre>
      </div>
    </div>
    <p class="diff-reason">{{ block.reason }}</p>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { DiffBlock } from "@/types/result";

const props = defineProps<{
  block: DiffBlock;
}>();

const sectionMap: Record<DiffBlock["section"], string> = {
  summary: "个人摘要",
  experience: "工作经历",
  education: "教育经历",
  projects: "项目经历",
  skills: "技能",
};

const changeTypeMap: Record<string, string> = {
  rewrite: "改写优化",
  reorder: "重组整理",
};

const sectionLabel = computed(() => sectionMap[props.block.section] || props.block.section);
const changeTypeLabel = computed(() => changeTypeMap[props.block.change_type] || props.block.change_type);
</script>
