import { createRouter, createWebHistory } from "vue-router";

import UploadPage from "@/pages/UploadPage.vue";
import JobPage from "@/pages/JobPage.vue";
import ResultPage from "@/pages/ResultPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "upload", component: UploadPage },
    { path: "/jobs/:jobId", name: "job", component: JobPage, props: true },
    { path: "/results/:jobId", name: "result", component: ResultPage, props: true },
  ],
});

export default router;
