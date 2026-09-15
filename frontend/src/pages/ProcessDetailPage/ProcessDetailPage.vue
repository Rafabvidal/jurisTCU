<script setup lang="ts">
import { ArrowUp } from 'lucide-vue-next'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import BaseCard from '@/shared/components/ui/BaseCard.vue'
import EmptyPanel from '@/shared/components/ui/EmptyPanel.vue'

import { normalizeDesfecho, normalizeResultadoReclamante, normalizeStatus } from '@/utils/fieldNormalizers'
import ProcessTimeline from './components/ProcessTimeline.vue'
import { useProcessoDetalhe } from './composables/useProcessoDetalhe'

const route = useRoute()

const showBackToTop = ref(false)

function handleScroll() {
  showBackToTop.value = window.scrollY > 300
}

function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  })
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const numeroProcesso = computed(() => String(route.params.numeroProcesso ?? ''))
const grau = computed(() => String(route.params.grau ?? ''))
const hasValidParams = computed(() => Boolean(numeroProcesso.value && grau.value))

const { data, isLoading, isError, error } = useProcessoDetalhe(
  numeroProcesso,
  grau,
  hasValidParams,
)

const processDetail = computed(() => data.value ?? null)
const sortedMovimentos = computed(() =>
  [...(processDetail.value?.movimentos ?? [])].sort(
    (left, right) => new Date(left.data_hora).getTime() - new Date(right.data_hora).getTime(),
  ),
)

const externalProcessUrl = computed(() =>
  `https://pje.trt6.jus.br/consultaprocessual/detalhe-processo/${encodeURIComponent(
    numeroProcesso.value,
  )}`,
)

function formatDate(value?: string | null): string {
  if (!value) return 'Não informado'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' }).format(date)
}

function formatCurrency(value?: string | null): string {
  if (!value) return 'Não informado'
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) return value
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(parsed)
}
</script>

<template>
  <section class="detail-page">
    <div class="hero-shell" v-motion :initial="{ opacity: 0, y: 12 }" :enter="{ opacity: 1, y: 0 }">
      <div class="hero-copy">
        <p class="eyebrow">Detalhes do processo</p>
        <h1>{{ processDetail?.numero_processo ?? numeroProcesso }}</h1>
        <p class="hero-description">
          Visão consolidada do processo, com análise, assuntos e movimentos cronológicos.
        </p>
      </div>

      <div class="hero-actions">
        <RouterLink class="back-link" to="/">Voltar à busca</RouterLink>
        <a
          class="secondary-link"
          :href="externalProcessUrl"
          target="_blank"
          rel="noreferrer noopener"
        >
          Abrir no TRT-6
        </a>
      </div>
    </div>

    <div v-if="!hasValidParams" class="state-block" v-motion :initial="{ opacity: 0, y: 12 }" :enter="{ opacity: 1, y: 0 }">
      <EmptyPanel
        title="Parâmetros inválidos"
        description="A rota de detalhe precisa de número do processo e grau para carregar os dados."
      />
    </div>

    <div v-else-if="isLoading" class="state-block" v-motion :initial="{ opacity: 0, y: 12 }" :enter="{ opacity: 1, y: 0 }">
      <EmptyPanel
        title="Carregando detalhe do processo…"
        description="Buscando o processo selecionado e seus movimentos persistidos."
      />
    </div>

    <div v-else-if="isError" class="state-block" v-motion :initial="{ opacity: 0, y: 12 }" :enter="{ opacity: 1, y: 0 }">
      <EmptyPanel
        title="Não foi possível carregar o processo"
        :description="error?.message ?? 'Tente novamente em instantes.'"
      />
    </div>

    <div v-else-if="!processDetail" class="state-block" v-motion :initial="{ opacity: 0, y: 12 }" :enter="{ opacity: 1, y: 0 }">
      <EmptyPanel
        title="Processo não encontrado"
        description="Verifique o número informado e tente novamente."
      />
    </div>

    <div v-else class="content-grid" v-motion :initial="{ opacity: 0, y: 14 }" :enter="{ opacity: 1, y: 0, transition: { delay: 90 } }">
      <div class="main-column">
        <BaseCard>
          <header class="summary-head">
            <div>
              <p class="section-label">Resumo geral</p>
              <h2>{{ processDetail.classe?.nome ?? 'Classe não informada' }}</h2>
            </div>
            <span class="status-chip" :data-state="processDetail.em_andamento ? 'active' : 'inactive'">
              {{ processDetail.em_andamento ? 'Em andamento' : 'Finalizado' }}
            </span>
          </header>

          <dl class="info-grid">
            <div>
              <dt>Tribunal</dt>
              <dd>{{ processDetail.tribunal }}</dd>
            </div>
            <div>
              <dt>Grau</dt>
              <dd>{{ processDetail.grau }}</dd>
            </div>
            <div>
              <dt>Órgão julgador</dt>
              <dd>{{ processDetail.orgao_julgador?.nome ?? 'Não informado' }}</dd>
            </div>
            <div>
              <dt>Ajuizamento</dt>
              <dd>{{ formatDate(processDetail.data_ajuizamento) }}</dd>
            </div>
            <div>
              <dt>Última atualização</dt>
              <dd>{{ formatDate(processDetail.data_hora_ultima_atualizacao) }}</dd>
            </div>
            <div>
              <dt>Valor da causa</dt>
              <dd>{{ formatCurrency(processDetail.analise?.valor_causa) }}</dd>
            </div>
          </dl>
        </BaseCard>

        <BaseCard>
          <p class="section-label">Resumo</p>
          <h2>Contexto consolidado</h2>
          <p class="body-copy">
            {{ processDetail.analise?.resumo ?? 'Resumo não informado para este processo.' }}
          </p>
        </BaseCard>

        <BaseCard>
          <p class="section-label">Decisão</p>
          <h2>Resultado e fundamentos</h2>
          <p class="body-copy">
            {{ processDetail.analise?.decisao ?? 'Decisão não informada para este processo.' }}
          </p>

          <dl class="decision-grid">
            <div>
              <dt>Status</dt>
              <dd>{{ normalizeStatus(processDetail.analise?.status) }}</dd>
            </div>
            <div>
              <dt>Desfecho</dt>
              <dd>{{ normalizeDesfecho(processDetail.analise?.desfecho) }}</dd>
            </div>
            <div>
              <dt>Resultado reclamante</dt>
              <dd>{{ normalizeResultadoReclamante(processDetail.analise?.resultado_reclamante) }}</dd>
            </div>
            <div>
              <dt>Custas totais</dt>
              <dd>{{ formatCurrency(processDetail.analise?.custas_valor_total) }}</dd>
            </div>
          </dl>
        </BaseCard>

        <ProcessTimeline :movimentos="sortedMovimentos" />
      </div>

      <aside class="side-column">
        <BaseCard>
          <p class="section-label">Assuntos</p>
          <h2>Tópicos identificados</h2>
          <ul v-if="processDetail.assuntos.length" class="pill-list">
            <li v-for="assunto in processDetail.assuntos" :key="assunto.codigo">{{ assunto.nome }}</li>
          </ul>
          <p v-else class="body-copy subtle">Nenhum assunto foi associado a este processo.</p>
        </BaseCard>

        <BaseCard>
          <p class="section-label">Palavras-chave</p>
          <h2>Principais sinais</h2>
          <ul v-if="processDetail.analise?.palavras_chave?.length" class="pill-list">
            <li v-for="palavra in processDetail.analise.palavras_chave" :key="palavra.id ?? palavra.nome">{{ palavra.nome }}</li>
          </ul>
          <p v-else class="body-copy subtle">Nenhuma palavra-chave disponível.</p>
        </BaseCard>

        <BaseCard>
          <p class="section-label">Identificação</p>
          <h2>Dados de navegação</h2>
          <dl class="stacked-list">
            <div>
              <dt>Número do processo</dt>
              <dd>{{ processDetail.numero_processo }}</dd>
            </div>
            <div>
              <dt>Grau público</dt>
              <dd>{{ processDetail.grau }}</dd>
            </div>
            <div>
              <dt>Movimentos persistidos</dt>
              <dd>{{ sortedMovimentos.length }}</dd>
            </div>
          </dl>
        </BaseCard>
      </aside>
    </div>
  </section>

  <!-- Back to top button -->
  <button 
    v-show="showBackToTop" 
    class="back-to-top" 
    aria-label="Voltar ao topo" 
    @click="scrollToTop"
  >
    <ArrowUp class="icon-up" />
  </button>
</template>

<style scoped>
.detail-page {
  display: grid;
  gap: 1rem;
}

.hero-shell {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  padding: 1.25rem 1.35rem;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, rgba(28, 92, 145, 0.12), rgba(216, 91, 45, 0.08));
  border: 1px solid rgba(28, 92, 145, 0.12);
}

.eyebrow,
.section-label {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.74rem;
  color: var(--brand-strong);
  font-weight: 700;
}

h1 {
  margin: 0.25rem 0 0;
  font-family: var(--font-display);
  color: var(--text-strong);
  font-size: clamp(1.5rem, 2.5vw, 2.2rem);
}

.hero-description {
  margin: 0.45rem 0 0;
  color: var(--text-muted);
  max-width: 60ch;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.back-link,
.secondary-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 0.9rem;
  border-radius: var(--radius-sm);
  text-decoration: none;
  font-weight: 700;
  font-size: 0.88rem;
  transition: transform 140ms ease, background 140ms ease, border-color 140ms ease;
}

.back-link {
  background: var(--bg-surface);
  color: var(--text-body);
  border: 1px solid var(--line);
}

.secondary-link {
  background: rgba(216, 91, 45, 0.08);
  color: #8d3d1f;
  border: 1px solid rgba(216, 91, 45, 0.18);
}

.back-link:hover,
.secondary-link:hover {
  transform: translateY(-1px);
}

.state-block {
  margin-top: 0.25rem;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.85fr);
  gap: 1rem;
  align-items: start;
}

.main-column,
.side-column {
  display: grid;
  gap: 1rem;
}

.summary-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

h2 {
  margin: 0.25rem 0 0;
  font-family: var(--font-display);
  color: var(--text-strong);
}

.status-chip {
  border-radius: 999px;
  padding: 0.35rem 0.7rem;
  font-size: 0.82rem;
  font-weight: 700;
  white-space: nowrap;
}

.status-chip[data-state='active'] {
  background: rgba(28, 92, 145, 0.08);
  color: var(--brand-strong);
}

.status-chip[data-state='inactive'] {
  background: rgba(127, 76, 43, 0.1);
  color: #8d3d1f;
}

.info-grid,
.decision-grid,
.stacked-list {
  display: grid;
  gap: 0.85rem;
  margin: 1rem 0 0;
}

.info-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.decision-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.stacked-list {
  grid-template-columns: 1fr;
}

dt {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.8rem;
}

dd {
  margin: 0.18rem 0 0;
  color: var(--text-strong);
  font-weight: 600;
}

.body-copy {
  margin: 0.9rem 0 0;
  color: var(--text-body);
  line-height: 1.6;
}

.subtle {
  color: var(--text-muted);
}

.pill-list {
  list-style: none;
  margin: 0.9rem 0 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pill-list li {
  border: 1px solid var(--line);
  background: var(--bg-soft);
  color: var(--text-body);
  padding: 0.32rem 0.6rem;
  border-radius: 999px;
  font-size: 0.82rem;
}

@media (max-width: 980px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .hero-shell {
    flex-direction: column;
    align-items: flex-start;
  }

  .info-grid,
  .decision-grid {
    grid-template-columns: 1fr;
  }
}

/* Back to top button styled premium */
.back-to-top {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 999px;
  background: var(--brand-strong);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 16px rgba(15, 45, 87, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 99;
  transition: transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1), background-color 200ms ease, box-shadow 200ms ease;
  animation: scaleIn 250ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.back-to-top:hover {
  background: #0d274c;
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 6px 20px rgba(15, 45, 87, 0.4);
}

.back-to-top:active {
  transform: translateY(-1px) scale(0.98);
}

.icon-up {
  width: 1.2rem;
  height: 1.2rem;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.5);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>