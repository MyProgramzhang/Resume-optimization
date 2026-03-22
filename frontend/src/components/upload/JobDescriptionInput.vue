<template>
  <div class="field-group">
    <label class="field-label" for="jobDescription">职位描述</label>
    <textarea
      id="jobDescription"
      :value="modelValue"
      rows="8"
      placeholder="请粘贴目标岗位的职位描述。"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string;
}>();

defineEmits<{
  "update:modelValue": [value: string];
}>();
</script>
