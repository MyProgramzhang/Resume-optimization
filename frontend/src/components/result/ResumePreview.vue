<template>
  <section class="card resume-panel">
    <div class="status-head">
      <div>
        <p class="eyebrow">{{ title }}</p>
        <h2>{{ resume.basics.name || "候选人" }}</h2>
      </div>
      <span class="resume-panel-tag" :class="{ 'resume-panel-tag--changed': highlightChanges }">
        {{ highlightChanges ? "修改后" : "原简历" }}
      </span>
    </div>

    <p v-if="basicsLine" class="resume-basics">{{ basicsLine }}</p>

    <div v-if="resume.summary" class="resume-section">
      <h3>个人摘要</h3>
      <p v-html="renderText(resume.summary, compareResume?.summary || '')"></p>
    </div>

    <div v-if="resume.experience.length" class="resume-section">
      <h3>工作经历</h3>
      <article v-for="item in resume.experience" :key="item.block_id" class="resume-item">
        <div class="resume-item-head">
          <strong v-html="renderText(item.title || '岗位', originalExperienceMap.get(item.block_id)?.title || '')"></strong>
          <span v-html="renderText(item.company, originalExperienceMap.get(item.block_id)?.company || '')"></span>
        </div>
        <p class="meta-line" v-html="renderText(formatDateRange(item.start_date, item.end_date), formatDateRange(originalExperienceMap.get(item.block_id)?.start_date || '', originalExperienceMap.get(item.block_id)?.end_date || ''))"></p>
        <ul>
          <li
            v-for="(bullet, index) in item.bullets"
            :key="`${item.block_id}-${index}-${bullet}`"
            v-html="renderText(bullet, originalExperienceMap.get(item.block_id)?.bullets?.[index] || '')"
          ></li>
        </ul>
      </article>
    </div>

    <div v-if="resume.education.length" class="resume-section">
      <h3>教育经历</h3>
      <article v-for="item in resume.education" :key="item.block_id" class="resume-item">
        <div class="resume-item-head">
          <strong v-html="renderText(item.school, originalEducationMap.get(item.block_id)?.school || '')"></strong>
          <span
            v-html="renderText(
              [item.degree, item.major].filter(Boolean).join(' / '),
              [originalEducationMap.get(item.block_id)?.degree || '', originalEducationMap.get(item.block_id)?.major || '']
                .filter(Boolean)
                .join(' / '),
            )"
          ></span>
        </div>
        <p
          class="meta-line"
          v-html="renderText(
            formatDateRange(item.start_date, item.end_date),
            formatDateRange(originalEducationMap.get(item.block_id)?.start_date || '', originalEducationMap.get(item.block_id)?.end_date || ''),
          )"
        ></p>
      </article>
    </div>

    <div v-if="resume.projects.length" class="resume-section">
      <h3>项目经历</h3>
      <article v-for="item in resume.projects" :key="item.block_id" class="resume-item">
        <div class="resume-item-head">
          <strong v-html="renderText(item.name, originalProjectMap.get(item.block_id)?.name || '')"></strong>
          <span v-html="renderText(item.role, originalProjectMap.get(item.block_id)?.role || '')"></span>
        </div>
        <p
          class="meta-line"
          v-html="renderText(
            formatDateRange(item.start_date, item.end_date),
            formatDateRange(originalProjectMap.get(item.block_id)?.start_date || '', originalProjectMap.get(item.block_id)?.end_date || ''),
          )"
        ></p>
        <ul>
          <li
            v-for="(bullet, index) in item.bullets"
            :key="`${item.block_id}-${index}-${bullet}`"
            v-html="renderText(bullet, originalProjectMap.get(item.block_id)?.bullets?.[index] || '')"
          ></li>
        </ul>
      </article>
    </div>

    <div v-if="resume.skills.length" class="resume-section">
      <h3>技能</h3>
      <ul class="skill-list">
        <li v-for="(group, index) in resume.skills" :key="`${group.category}-${index}`">
          <span
            v-html="renderText(
              `${group.category}：${group.items.join('，')}`,
              `${compareSkillGroup(group.category, index)?.category || group.category}：${compareSkillGroup(group.category, index)?.items?.join('，') || ''}`,
            )"
          ></span>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { EducationItem, ExperienceItem, ProjectItem, ResumeSchema, SkillGroup } from "@/types/resume";

const props = withDefaults(
  defineProps<{
    resume: ResumeSchema;
    title: string;
    compareResume?: ResumeSchema | null;
    highlightChanges?: boolean;
  }>(),
  {
    compareResume: null,
    highlightChanges: false,
  },
);

const originalExperienceMap = computed(() => toMap(props.compareResume?.experience));
const originalEducationMap = computed(() => toMap(props.compareResume?.education));
const originalProjectMap = computed(() => toMap(props.compareResume?.projects));

const basicsLine = computed(() =>
  [props.resume.basics.location, props.resume.basics.phone, props.resume.basics.email]
    .filter(Boolean)
    .join(" ｜ "),
);

function toMap<T extends { block_id: string }>(items: T[] | undefined): Map<string, T> {
  return new Map((items || []).map((item) => [item.block_id, item]));
}

function compareSkillGroup(category: string, index: number): SkillGroup | undefined {
  if (!props.compareResume) {
    return undefined;
  }
  return props.compareResume.skills.find((group) => group.category === category) || props.compareResume.skills[index];
}

function formatDateRange(start: string, end: string): string {
  return [start, end].filter(Boolean).join(" - ");
}

function renderText(current: string, original: string): string {
  const safeCurrent = escapeHtml(current || "");
  if (!props.highlightChanges || !props.compareResume || !original || current === original) {
    return safeCurrent;
  }

  const newTokens = tokenize(current);
  const oldTokens = tokenize(original);
  const diff = buildTokenDiff(oldTokens, newTokens);
  return diff
    .map((segment) => {
      const text = escapeHtml(segment.text);
      return segment.changed ? `<span class="diff-added">${text}</span>` : text;
    })
    .join("");
}

type DiffSegment = {
  text: string;
  changed: boolean;
};

function tokenize(text: string): string[] {
  const tokens = text.match(/[\u4e00-\u9fff]|[A-Za-z0-9]+|\s+|[^\sA-Za-z0-9\u4e00-\u9fff]/g);
  return tokens && tokens.length ? tokens : [text];
}

function buildTokenDiff(oldTokens: string[], newTokens: string[]): DiffSegment[] {
  const rows = oldTokens.length + 1;
  const cols = newTokens.length + 1;
  const dp: number[][] = Array.from({ length: rows }, () => Array(cols).fill(0));

  for (let i = oldTokens.length - 1; i >= 0; i -= 1) {
    for (let j = newTokens.length - 1; j >= 0; j -= 1) {
      if (oldTokens[i] === newTokens[j]) {
        dp[i][j] = dp[i + 1][j + 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1]);
      }
    }
  }

  const segments: DiffSegment[] = [];
  let i = 0;
  let j = 0;

  while (i < oldTokens.length && j < newTokens.length) {
    if (oldTokens[i] === newTokens[j]) {
      pushSegment(segments, newTokens[j], false);
      i += 1;
      j += 1;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      i += 1;
    } else {
      pushSegment(segments, newTokens[j], true);
      j += 1;
    }
  }

  while (j < newTokens.length) {
    pushSegment(segments, newTokens[j], true);
    j += 1;
  }

  return segments;
}

function pushSegment(segments: DiffSegment[], text: string, changed: boolean): void {
  const last = segments[segments.length - 1];
  if (last && last.changed === changed) {
    last.text += text;
    return;
  }
  segments.push({ text, changed });
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
</script>
