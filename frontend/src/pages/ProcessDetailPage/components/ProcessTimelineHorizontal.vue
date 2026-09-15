<script setup lang="ts">
import { computed, ref } from 'vue';

import BaseCard from '@/shared/components/ui/BaseCard.vue';
import type { MovimentoDTO } from '@/shared/types/api';

const props = defineProps<{
  movimentos: MovimentoDTO[]
}>();

const expandedIndexes = ref<Set<number>>(new Set());

const sortedMovimentos = computed(() =>
  [...props.movimentos].sort(
    (left, right) => new Date(left.data_hora).getTime() - new Date(right.data_hora).getTime(),
  ),
);

const timelineStructure = computed(() => {
  const sorted = sortedMovimentos.value;
  if (sorted.length === 0) return { first: undefined, middle: [], last: undefined };
  if (sorted.length === 1) return { first: sorted[0], middle: [], last: undefined };
  
  return {
    first: sorted[0],
    middle: sorted.slice(1, -1),
    last: sorted[sorted.length - 1],
  };
});

function formatDate(value?: string): string {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

function formatShortDate(value?: string): string {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('pt-BR', {
    month: 'short',
    day: 'numeric',
  }).format(date);
}

function calculateTimeDiff(from?: string, to?: string): string {
  if (!from || !to) return '';
  const fromDate = new Date(from);
  const toDate = new Date(to);
  
  if (Number.isNaN(fromDate.getTime()) || Number.isNaN(toDate.getTime())) return '';
  
  const diffMs = toDate.getTime() - fromDate.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Mesmo dia';
  if (diffDays === 1) return '1 dia';
  if (diffDays < 30) return `${diffDays} dias`;
  
  const diffMonths = Math.floor(diffDays / 30);
  if (diffMonths === 1) return '1 mês';
  if (diffMonths < 12) return `${diffMonths} meses`;
  
  const diffYears = Math.floor(diffMonths / 12);
  return diffYears === 1 ? '1 ano' : `${diffYears} anos`;
}
</script>

<template>
  <BaseCard>
    <header class="timeline-header">
      <div>
        <p class="eyebrow">Linha do tempo</p>
        <h2>Movimentos do processo</h2>
      </div>
      <span class="counter">{{ sortedMovimentos.length }} eventos</span>
    </header>

    <div v-if="sortedMovimentos.length === 0" class="empty-state">
      Nenhum movimento foi persistido para este processo ainda.
    </div>

    <div v-else class="horizontal-timeline">
      <!-- First Movement (Fixed Left) -->
      <div v-if="timelineStructure.first" class="timeline-section first">
        <div class="movement-card">
          <div class="marker first-marker"></div>
          <div class="content">
            <time class="date">{{ formatDate(timelineStructure.first.data_hora) }}</time>
            <h3>{{ timelineStructure.first.nome }}</h3>
            <p v-if="timelineStructure.first.orgao_julgador?.nome" class="orgao">
              {{ timelineStructure.first.orgao_julgador.nome }}
            </p>
          </div>
        </div>
        <p v-if="timelineStructure.middle.length > 0" class="section-label">Início</p>
      </div>

      <!-- Middle Movements (Expandable) -->
      <div v-if="timelineStructure.middle.length > 0" class="timeline-section middle">
        <div class="middle-container">
          <div class="middle-header">
            <div class="dots" aria-hidden="true">
              <span v-for="i in 3" :key="i" class="dot"></span>
            </div>
            <p class="middle-label">{{ timelineStructure.middle.length }} movimentos intermediários</p>
            <button
              class="toggle-btn"
              :aria-expanded="expandedIndexes.size > 0"
              @click="() => {
                if (expandedIndexes.size === 0) {
                  timelineStructure.middle.forEach((_, i) => expandedIndexes.add(i));
                } else {
                  expandedIndexes.clear();
                }
              }"
            >
              {{ expandedIndexes.size === 0 ? 'Expandir' : 'Recolher' }}
            </button>
          </div>

          <!-- Expanded middle items -->
          <div v-if="expandedIndexes.size > 0" class="middle-items">
            <div
              v-for="(movimento, index) in timelineStructure.middle"
              :key="`middle-${index}`"
              class="middle-item"
            >
              <div class="item-header">
                <div class="item-marker"></div>
                <div class="item-info">
                  <time class="item-date">{{ formatShortDate(movimento.data_hora) }}</time>
                  <h4>{{ movimento.nome }}</h4>
                </div>
                <!-- Time elapsed to next movement -->
                <div v-if="index < timelineStructure.middle.length - 1 && timelineStructure.middle[index + 1]" class="time-elapsed">
                  <span class="badge">{{ calculateTimeDiff(movimento.data_hora, timelineStructure.middle[index + 1]?.data_hora) }}</span>
                </div>
                <div v-else-if="timelineStructure.last" class="time-elapsed">
                  <span class="badge">{{ calculateTimeDiff(movimento.data_hora, timelineStructure.last?.data_hora) }}</span>
                </div>
              </div>
              <p v-if="movimento.orgao_julgador?.nome" class="item-orgao">
                {{ movimento.orgao_julgador.nome }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Last Movement (Fixed Right) -->
      <div v-if="timelineStructure.last" class="timeline-section last">
        <p class="section-label">Fim</p>
        <div class="movement-card">
          <div class="marker last-marker"></div>
          <div class="content">
            <time class="date">{{ formatDate(timelineStructure.last.data_hora) }}</time>
            <h3>{{ timelineStructure.last.nome }}</h3>
            <p v-if="timelineStructure.last.orgao_julgador?.nome" class="orgao">
              {{ timelineStructure.last.orgao_julgador.nome }}
            </p>
          </div>
        </div>
      </div>

      <!-- Time elapsed: first to last -->
      <div v-if="timelineStructure.middle.length > 0" class="total-duration">
        <p>
          <strong>Período total:</strong>
          {{ calculateTimeDiff(timelineStructure.first?.data_hora, timelineStructure.last?.data_hora) }}
        </p>
      </div>
    </div>
  </BaseCard>
</template>

<style scoped>
.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.74rem;
  color: var(--brand-strong);
  font-weight: 700;
}

h2 {
  margin: 0.25rem 0 0;
  font-family: var(--font-display);
  color: var(--text-strong);
}

.counter {
  border-radius: 999px;
  background: rgba(28, 92, 145, 0.08);
  color: var(--brand-strong);
  padding: 0.4rem 0.7rem;
  font-size: 0.82rem;
  font-weight: 700;
  white-space: nowrap;
}

.empty-state {
  border: 1px dashed var(--line-strong);
  border-radius: var(--radius-md);
  padding: 1rem;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.4);
}

.horizontal-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.timeline-section.first,
.timeline-section.last {
  flex-shrink: 0;
}

.section-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-weight: 600;
  margin: 0;
}

/* Movement Cards (First & Last) */
.movement-card {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  padding: 1rem;
  border-radius: var(--radius-md);
  background: rgba(28, 92, 145, 0.04);
  border: 1px solid var(--line);
}

.marker {
  width: 0.9rem;
  height: 0.9rem;
  border-radius: 999px;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.marker.first-marker,
.marker.last-marker {
  background: linear-gradient(135deg, var(--accent), var(--brand-strong));
  box-shadow: 0 0 0 4px rgba(28, 92, 145, 0.12);
}

.content {
  flex: 1;
}

.date {
  display: block;
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.content h3 {
  margin: 0;
  color: var(--text-strong);
  font-size: 1rem;
  font-weight: 600;
}

.orgao {
  margin: 0.35rem 0 0;
  font-size: 0.88rem;
  color: var(--text-body);
}

/* Middle Items Container */
.middle-container {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  padding: 1rem;
}

.middle-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--line);
}

.dots {
  display: flex;
  gap: 0.35rem;
}

.dot {
  width: 0.35rem;
  height: 0.35rem;
  border-radius: 999px;
  background: var(--text-muted);
  opacity: 0.6;
}

.middle-label {
  margin: 0;
  font-size: 0.88rem;
  color: var(--text-body);
  flex: 1;
  font-weight: 500;
}

.toggle-btn {
  background: none;
  border: 1px solid var(--line);
  padding: 0.35rem 0.7rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--brand-strong);
  cursor: pointer;
  transition: all 140ms ease;
  white-space: nowrap;
}

.toggle-btn:hover {
  background: rgba(28, 92, 145, 0.08);
  border-color: var(--brand-strong);
}

/* Expanded Middle Items */
.middle-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.middle-item {
  padding: 0.75rem;
  background: rgba(28, 92, 145, 0.02);
  border-left: 2px solid var(--brand-strong);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.item-header {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.item-marker {
  width: 0.6rem;
  height: 0.6rem;
  border-radius: 999px;
  background: var(--brand-strong);
  flex-shrink: 0;
  margin-top: 0.3rem;
}

.item-info {
  flex: 1;
}

.item-date {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: capitalize;
  font-weight: 500;
}

.item-header h4 {
  margin: 0.15rem 0 0;
  font-size: 0.92rem;
  color: var(--text-strong);
  font-weight: 500;
}

.time-elapsed {
  display: flex;
  align-items: center;
}

.badge {
  font-size: 0.7rem;
  background: rgba(28, 92, 145, 0.12);
  color: var(--brand-strong);
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
  font-weight: 600;
  white-space: nowrap;
}

.item-orgao {
  margin: 0.4rem 0 0 1.1rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* Total Duration */
.total-duration {
  padding: 0.75rem 1rem;
  background: rgba(28, 92, 145, 0.08);
  border-left: 3px solid var(--brand-strong);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  margin-top: 0.5rem;
}

.total-duration p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-strong);
}

.total-duration strong {
  color: var(--brand-strong);
  font-weight: 600;
}

/* Responsive */
@media (max-width: 768px) {
  .horizontal-timeline {
    gap: 0.75rem;
  }

  .movement-card {
    padding: 0.75rem;
  }

  .middle-header {
    flex-wrap: wrap;
  }

  .toggle-btn {
    order: 3;
    flex-basis: 100%;
    width: 100%;
    margin-top: 0.5rem;
  }
}
</style>
