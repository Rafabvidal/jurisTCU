<script setup lang="ts">
import { ChevronDown, ChevronUp, ChevronsUpDown, Clock } from 'lucide-vue-next';
import { computed, ref } from 'vue';

import BaseCard from '@/shared/components/ui/BaseCard.vue';
import type { MovimentoDTO } from '@/shared/types/api';

const props = defineProps<{
  movimentos: MovimentoDTO[]
}>()

const isExpanded = ref(false)

const sortedMovimentos = computed(() =>
  [...props.movimentos].sort(
    (left, right) => new Date(left.data_hora).getTime() - new Date(right.data_hora).getTime(),
  ),
)

const displayedMovimentos = computed<MovimentoDTO[]>(() => {
  const sorted = sortedMovimentos.value
  if (sorted.length <= 2 || isExpanded.value) {
    return sorted
  }
  const first = sorted[0]
  const last = sorted[sorted.length - 1]
  const result: MovimentoDTO[] = []
  if (first) result.push(first)
  if (last) result.push(last)
  return result
})

const hiddenCount = computed(() => {
  if (sortedMovimentos.value.length <= 2) return 0
  return sortedMovimentos.value.length - 2
})

const totalProcessDuration = computed(() => {
  const sorted = sortedMovimentos.value
  if (sorted.length <= 1) return ''
  const first = sorted[0]
  const last = sorted[sorted.length - 1]
  if (!first || !last) return ''
  return formatTimeDifference(last.data_hora, first.data_hora)
})

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function formatTimeDifference(laterStr: string, earlierStr: string): string {
  const later = new Date(laterStr)
  const earlier = new Date(earlierStr)
  if (Number.isNaN(later.getTime()) || Number.isNaN(earlier.getTime())) return ''
  
  const diffMs = later.getTime() - earlier.getTime()
  if (diffMs < 0) return '0 dias'
  
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  if (diffDays === 0) {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    if (diffHours === 0) {
      return 'alguns minutos'
    }
    return `${diffHours} ${diffHours === 1 ? 'hora' : 'horas'}`
  }
  
  if (diffDays < 30) {
    return `${diffDays} ${diffDays === 1 ? 'dia' : 'dias'}`
  }
  
  const diffMonths = Math.floor(diffDays / 30)
  const remainingDays = diffDays % 30
  
  if (diffMonths < 12) {
    if (remainingDays === 0) {
      return `${diffMonths} ${diffMonths === 1 ? 'mês' : 'meses'}`
    }
    return `${diffMonths} ${diffMonths === 1 ? 'mês' : 'meses'} e ${remainingDays} ${remainingDays === 1 ? 'dia' : 'dias'}`
  }
  
  const diffYears = Math.floor(diffMonths / 12)
  const remainingMonths = diffMonths % 12
  
  if (remainingMonths === 0) {
    return `${diffYears} ${diffYears === 1 ? 'ano' : 'anos'}`
  }
  return `${diffYears} ${diffYears === 1 ? 'ano' : 'anos'} e ${remainingMonths} ${remainingMonths === 1 ? 'mês' : 'meses'}`
}
</script>

<template>
  <BaseCard>
    <header class="timeline-header">
      <div>
        <p class="eyebrow">Linha do tempo</p>
        <h2>Movimentos do processo</h2>
      </div>
      <div class="header-actions">
        <span class="counter">{{ sortedMovimentos.length }} eventos</span>
        <button 
          v-if="sortedMovimentos.length > 2" 
          class="header-toggle-btn"
          @click="isExpanded = !isExpanded"
        >
          <ChevronUp v-if="isExpanded" class="icon-btn-size" />
          <ChevronDown v-else class="icon-btn-size" />
          <span>{{ isExpanded ? 'Recolher tudo' : 'Expandir tudo' }}</span>
        </button>
      </div>
    </header>

    <div v-if="sortedMovimentos.length === 0" class="empty-state">
      Nenhum movimento foi persistido para este processo ainda.
    </div>

    <ol v-else class="timeline-list">
      <template v-for="(movimento, index) in displayedMovimentos" :key="`${movimento.codigo}-${movimento.data_hora}`">
        <li class="timeline-item">
          <div class="marker" aria-hidden="true"></div>
          <div class="content">
            <p class="date">{{ formatDate(movimento.data_hora) }}</p>
            <h3>{{ movimento.nome }}</h3>
            <p v-if="movimento.orgao_julgador?.nome" class="orgao">
              {{ movimento.orgao_julgador.nome }}
            </p>
          </div>
        </li>

        <!-- Time elapsed badge between sequential events -->
        <li 
          v-if="isExpanded && index < displayedMovimentos.length - 1" 
          class="timeline-time-bridge"
        >
          <div class="bridge-line"></div>
          <div class="time-elapsed-badge">
            <Clock class="icon-inline" />
            <span>+ {{ formatTimeDifference(displayedMovimentos[index + 1]?.data_hora || '', movimento.data_hora) }}</span>
          </div>
        </li>

        <!-- Expandable middle section trigger -->
        <li 
          v-if="!isExpanded && index === 0 && hiddenCount > 0" 
          class="timeline-expand-item"
        >
          <div class="bridge-line dashed"></div>
          <div class="expand-action-card" @click="isExpanded = true">
            <button class="expand-btn">
              <ChevronsUpDown class="icon-btn-size" />
              <span>Mostrar {{ hiddenCount }} eventos intermediários</span>
              <span class="btn-duration">({{ totalProcessDuration }})</span>
            </button>
          </div>
          <div class="bridge-line dashed"></div>
        </li>
      </template>
    </ol>
  </BaseCard>
</template>

<style scoped>
.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
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

.timeline-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 1rem;
}

.timeline-item {
  display: grid;
  grid-template-columns: 0.9rem minmax(0, 1fr);
  gap: 0.75rem;
  align-items: flex-start;
}

.marker {
  width: 0.9rem;
  height: 0.9rem;
  margin-top: 0.3rem;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent), var(--brand-strong));
  box-shadow: 0 0 0 4px rgba(28, 92, 145, 0.08);
}

.content {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--line);
}

.timeline-item:last-child .content {
  padding-bottom: 0;
  border-bottom: 0;
}

.date {
  margin: 0;
  font-size: 0.82rem;
  color: var(--text-muted);
}

h3 {
  margin: 0.25rem 0 0;
  color: var(--text-strong);
  font-size: 1rem;
}

.orgao {
  margin: 0.35rem 0 0;
  color: var(--text-body);
}

@media (max-width: 700px) {
  .timeline-header {
    flex-direction: column;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-toggle-btn {
  background: var(--bg-surface);
  border: 1px solid var(--line);
  color: var(--text-body);
  border-radius: var(--radius-sm, 6px);
  padding: 0.38rem 0.8rem;
  font-size: 0.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
  transition: all 140ms ease;
}

.header-toggle-btn:hover {
  background: var(--bg-soft);
  border-color: var(--brand-strong);
  color: var(--brand-strong);
  transform: translateY(-0.5px);
}

.icon-btn-size {
  width: 0.95rem;
  height: 0.95rem;
}

.icon-inline {
  width: 0.82rem;
  height: 0.82rem;
  margin-right: 0.2rem;
}

/* Time elapsed bridges and connector lines */
.timeline-time-bridge,
.timeline-expand-item {
  display: grid;
  grid-template-columns: 0.9rem minmax(0, 1fr);
  gap: 0.75rem;
  align-items: center;
}

.timeline-time-bridge {
  margin: -0.25rem 0;
}

.timeline-expand-item {
  margin: 0.5rem 0;
}

.bridge-line {
  width: 2px;
  height: 100%;
  background: var(--line, #e2e8f0);
  justify-self: center;
  min-height: 1.5rem;
}

.bridge-line.dashed {
  width: 2px;
  height: 1.5rem;
  border-left: 2px dashed var(--line-strong, #cbd5e1);
  background: transparent;
  justify-self: center;
}

.time-elapsed-badge {
  font-size: 0.76rem;
  color: var(--brand-strong);
  background: rgba(28, 92, 145, 0.05);
  border: 1px dashed rgba(28, 92, 145, 0.2);
  padding: 0.22rem 0.6rem;
  border-radius: 999px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  width: fit-content;
  animation: fadeIn 300ms ease;
}

/* Collapsible expansion card */
.expand-action-card {
  cursor: pointer;
  background: linear-gradient(135deg, rgba(28, 92, 145, 0.04), rgba(216, 91, 45, 0.02));
  border: 1px dashed rgba(28, 92, 145, 0.25);
  border-radius: var(--radius-md, 8px);
  padding: 0.75rem 1.1rem;
  transition: all 200ms ease;
  display: flex;
  align-items: center;
  width: fit-content;
  animation: fadeIn 300ms ease;
}

.expand-action-card:hover {
  background: linear-gradient(135deg, rgba(28, 92, 145, 0.08), rgba(216, 91, 45, 0.04));
  border-color: var(--brand-strong);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(28, 92, 145, 0.06);
}

.expand-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--brand-strong);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-icon {
  font-size: 1rem;
  transition: transform 200ms ease;
}

.expand-action-card:hover .btn-icon {
  transform: translateY(2px);
}

.btn-duration {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 500;
  margin-left: 0.25rem;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>