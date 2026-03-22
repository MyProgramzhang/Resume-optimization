<template>
  <section class="card">
    <p class="eyebrow">修改摘要</p>
    <h2>本次优化做了什么</h2>
    <ul class="summary-list">
      <li v-for="item in items" :key="item">{{ item }}</li>
    </ul>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  items: string[];
}>();
</script>
