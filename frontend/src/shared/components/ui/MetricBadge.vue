<script setup lang="ts">
const props = defineProps<{ score: number }>()

const colorClass = props.score >= 0.9 ? 'high' : props.score >= 0.8 ? 'medium' : 'low'
</script>

<template>
  <div class="metric-badge" :class="colorClass">{{ Math.round(score * 100) }}% similar</div>
</template>

<style scoped>
.metric-badge {
  padding: 0.3rem 0.7rem;
  border-radius: var(--radius-xl);
  border: 1px solid transparent;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.high {
  color: #0f4f46;
  background: var(--accent-soft);
  border-color: #bce8dd;
}

.medium {
  color: #7a4c08;
  background: #fde9c7;
  border-color: #f0d7ab;
}

.low {
  color: #6b2330;
  background: #fdd7de;
  border-color: #efbdc7;
}
</style>
