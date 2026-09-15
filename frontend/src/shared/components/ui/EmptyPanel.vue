<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()
</script>

<template>
  <section class="empty-panel">
    <h2>{{ title }}</h2>
    <p>{{ description }}</p>
  </section>
</template>

<style scoped>
.empty-panel {
  border: 1px dashed var(--line-strong);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.55);
  text-align: center;
  padding: 2rem 1.1rem;
}

.empty-panel h2 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
  font-size: 1.2rem;
}

.empty-panel p {
  margin: 0.65rem 0 0;
  color: var(--text-muted);
}
</style>
