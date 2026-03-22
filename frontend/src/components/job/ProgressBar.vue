<template>
  <div class="progress-track">
    <div class="progress-fill" :style="{ width: `${value}%` }"></div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  value: number;
}>();
</script>
