<template>
  <div class="field-group">
    <label class="field-label">优化模式</label>
    <div class="mode-grid">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        class="mode-card"
        :class="{ active: modelValue === option.value }"
        @click="$emit('update:modelValue', option.value)"
      >
        <strong>{{ option.title }}</strong>
        <span>{{ option.description }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { JobMode } from "@/types/job";

defineProps<{
  modelValue: JobMode;
}>();

defineEmits<{
  "update:modelValue": [value: JobMode];
}>();

const options = [
  {
    value: "general" as const,
    title: "通用优化",
    description: "不依赖职位描述，提升表达清晰度、结构和专业度。",
  },
  {
    value: "jd_targeted" as const,
    title: "岗位定制",
    description: "结合职位描述定向优化简历内容。",
  },
];
</script>
