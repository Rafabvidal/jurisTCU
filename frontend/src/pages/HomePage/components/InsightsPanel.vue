<script setup lang="ts">
import { BarChart3, CircleDollarSign, Clock3, Gavel, Scale, TrendingUp } from 'lucide-vue-next'
import { computed } from 'vue'

import BaseCard from '@/shared/components/ui/BaseCard.vue'
import BaseChart from '@/shared/components/ui/charts/BaseChart.vue'
import {
  CHART_PALETTE_DESFECHO,
  CHART_PALETTE_RADIAL,
  CHART_PALETTE_RESULTADO,
  CHART_PALETTE_STATUS,
} from '@/shared/constants/charts'
import type { HomeInsights } from '@/shared/types/cases'
import { formatCurrencyBRL, formatMonthCount } from '@/shared/utils/formatters'

const props = defineProps<{ insights: HomeInsights }>()

const hasDesfechos = computed(
  () => props.insights.desfechoSeries.values.length > 0,
)
const hasStatus = computed(() => props.insights.statusSeries.values.length > 0)
const hasResultado = computed(
  () => props.insights.resultadoSeries.values.length > 0,
)
const hasValor = computed(() => props.insights.valorRadial.maximo > 0)
const hasArgumentos = computed(
  () => props.insights.kpis.palavrasChavesRelevantes.length > 0,
)

const valorPercentual = computed(() => {
  const raw = props.insights.valorRadial.percentual
  if (!Number.isFinite(raw)) return 0
  return Math.min(100, Math.max(0, Math.round(raw)))
})

const COUNT_LABEL = 'casos'

function formatCount(value: number): string {
  return `${value} ${COUNT_LABEL}`
}
</script>

<template>
  <section class="insights-panel">
    <h2>Painel de insights</h2>

    <div class="top-inline-grid">
      <BaseCard>
        <p class="metric-title">
          <TrendingUp :size="16" /> Taxa de procedência
        </p>
        <div class="metric-value">{{ insights.kpis.taxaProcedencia }}%</div>
        <p class="metric-note">
          Calculada a partir dos {{ insights.kpis.totalCases }} processos retornados pela busca semântica.
        </p>
      </BaseCard>

      <BaseCard>
        <p class="metric-title">
          <Clock3 :size="16" /> Tempo médio
        </p>
        <div class="metric-value small">
          {{ formatMonthCount(insights.kpis.tempoMedioMeses) }}
        </div>
        <p class="metric-note">
          Tramitação calculada a partir das datas de ajuizamento e última atualização.
        </p>
      </BaseCard>
    </div>

    <BaseCard>
      <p class="metric-title">
        <Gavel :size="16" /> Distribuição por desfecho
      </p>
      <BaseChart v-if="hasDesfechos" type="donut" :series="insights.desfechoSeries.values"
        :labels="insights.desfechoSeries.labels" :colors="CHART_PALETTE_DESFECHO" :value-formatter="formatCount" />
      <p v-else class="metric-note">Sem desfechos registrados nos resultados.</p>
    </BaseCard>

    <BaseCard>
      <p class="metric-title">
        <Scale :size="16" /> Resultado do reclamante
      </p>
      <BaseChart v-if="hasResultado" type="bar" :series="[{ name: COUNT_LABEL, data: insights.resultadoSeries.values }]"
        :labels="insights.resultadoSeries.labels" :colors="CHART_PALETTE_RESULTADO" :value-formatter="formatCount" />
      <p v-else class="metric-note">Sem dados de resultado disponíveis.</p>
    </BaseCard>

    <BaseCard>
      <p class="metric-title">
        <CircleDollarSign :size="16" /> Valor médio
      </p>
      <BaseChart v-if="hasValor" type="radialBar" :series="[valorPercentual]" :colors="CHART_PALETTE_RADIAL"
        center-label="Valor médio" :center-value="formatCurrencyBRL(insights.valorRadial.atual)" />
      <p v-else class="metric-value small">{{ formatCurrencyBRL(insights.kpis.valorMedio) }}</p>
      <p class="metric-note">
        Máximo: {{ formatCurrencyBRL(insights.kpis.valorMaximo) }}
      </p>
    </BaseCard>

    <BaseCard>
      <p class="metric-title">
        <BarChart3 :size="16" /> Status do processo
      </p>
      <BaseChart v-if="hasStatus" type="donut" :series="insights.statusSeries.values"
        :labels="insights.statusSeries.labels" :colors="CHART_PALETTE_STATUS" :value-formatter="formatCount" />
      <p v-else class="metric-note">Sem status registrado nos resultados.</p>
    </BaseCard>

    <BaseCard>
      <p class="metric-title">
        <BarChart3 :size="16" /> Palavras-chave relevantes
      </p>
      <ul v-if="hasArgumentos">
        <li v-for="argumento in insights.kpis.palavrasChavesRelevantes" :key="argumento">
          {{ argumento }}
        </li>
      </ul>
      <p v-else class="metric-note">
        Nenhuma palavra-chave agregada para os resultados desta busca.
      </p>
    </BaseCard>
  </section>
</template>

<style scoped>
.insights-panel {
  display: grid;
  gap: 0.75rem;
}

.top-inline-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

h2 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
  letter-spacing: -0.02em;
}

.metric-title {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  font-weight: 700;
}

.metric-value {
  margin: 0.35rem 0 0;
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--brand-strong);
}

.metric-value.small {
  font-size: 1.25rem;
}

.metric-note {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
}

.inline-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

ul {
  margin: 0.55rem 0 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.35rem;
}

@media (max-width: 900px) {
  .top-inline-grid {
    grid-template-columns: 1fr;
  }

  .inline-grid {
    grid-template-columns: 1fr;
  }
}
</style>
