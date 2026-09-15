<script setup lang="ts">
import { ArrowRight, ExternalLink } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

import BaseCard from '@/shared/components/ui/BaseCard.vue'
import MetricBadge from '@/shared/components/ui/MetricBadge.vue'
import type { ProcessCase } from '@/shared/types/cases'

const props = defineProps<{ item: ProcessCase }>()

const PJE_CONSULTA_BASE_URL = 'https://pje.trt6.jus.br/consultaprocessual/detalhe-processo/'

function buildProcessoUrl(numeroProcesso: string): string {
  return `${PJE_CONSULTA_BASE_URL}${encodeURIComponent(numeroProcesso)}`
}

function buildProcessoDetalheTo(item: ProcessCase) {
  return {
    path: `/processos/${encodeURIComponent(item.numeroProcesso)}/${encodeURIComponent(item.grau)}`,
  }
}
</script>

<template>
  <BaseCard>
    <header class="card-head">
      <div>
        <p class="case-number">{{ item.numeroProcesso }}</p>
        <p class="case-meta">{{ item.tribunal }} - {{ item.orgaoJulgadorNome }}</p>
      </div>
      <MetricBadge :score="item.similaridade" />
    </header>

    <div class="card-actions">
      <RouterLink class="detail-process-link" :to="buildProcessoDetalheTo(item)">
        <span>Ver detalhes do processo</span>
        <ArrowRight :size="14" />
      </RouterLink>
      <a
        class="external-process-link"
        :href="buildProcessoUrl(props.item.numeroProcesso)"
        target="_blank"
        rel="noreferrer noopener"
        title="Abre a página oficial do processo no TRT-6. Você sairá da aplicação para consultar o andamento no PJe."
        aria-label="Abrir processo original no TRT-6 em uma nova aba"
      >
        <span>Abrir processo original no TRT-6</span>
        <ExternalLink :size="14" />
      </a>
    </div>

    <p class="summary">
      <strong>Síntese:</strong>
      {{ item.resumoCausa }}
    </p>

    <div class="tags">
      <span v-for="tag in item.palavrasChave" :key="`${item.numeroProcesso}-${tag}`">{{ tag }}</span>
    </div>
  </BaseCard>
</template>

<style scoped>
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.case-number {
  margin: 0;
  font-weight: 700;
  color: var(--brand-strong);
}

.case-meta {
  margin: 0.2rem 0 0;
  color: var(--text-muted);
  font-size: 0.86rem;
}

.card-actions {
  margin-top: 0.7rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.detail-process-link,
.external-process-link {
  margin-top: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  width: fit-content;
  padding: 0.42rem 0.7rem;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(216, 91, 45, 0.2);
  background: rgba(216, 91, 45, 0.08);
  color: #8d3d1f;
  font-size: 0.82rem;
  font-weight: 700;
  text-decoration: none;
  transition:
    transform 140ms ease,
    background 140ms ease,
    border-color 140ms ease;
}

.detail-process-link {
  border-color: rgba(28, 92, 145, 0.18);
  background: rgba(28, 92, 145, 0.08);
  color: var(--brand-strong);
}

.detail-process-link:hover {
  transform: translateY(-1px);
  background: rgba(28, 92, 145, 0.12);
  border-color: rgba(28, 92, 145, 0.3);
}

.external-process-link:hover {
  transform: translateY(-1px);
  background: rgba(216, 91, 45, 0.12);
  border-color: rgba(216, 91, 45, 0.3);
}

.detail-process-link:focus-visible {
  outline: 2px solid rgba(28, 92, 145, 0.45);
  outline-offset: 2px;
}

.external-process-link:focus-visible {
  outline: 2px solid rgba(216, 91, 45, 0.45);
  outline-offset: 2px;
}

.summary {
  margin: 0.75rem 0;
  line-height: 1.5;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.tags span {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--bg-soft);
  color: var(--text-body);
  font-size: 0.78rem;
  padding: 0.23rem 0.5rem;
}
</style>
