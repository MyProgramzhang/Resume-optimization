<template>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">本地简历优化工具</p>
        <h1>简历优化智能体</h1>
      </div>
      <RouterLink to="/" class="ghost-link">新建任务</RouterLink>
    </header>
    <main class="page-shell">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>
