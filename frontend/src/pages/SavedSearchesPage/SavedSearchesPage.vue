<script setup lang="ts">
import { SavedSearchesService } from '@/services/savedSearchesService'
import { queryKeys } from '@/services/queryKeys'
import BaseCard from '@/shared/components/ui/BaseCard.vue'
import EmptyPanel from '@/shared/components/ui/EmptyPanel.vue'
import type { SavedSearchDTO } from '@/shared/types/api'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { Clock3, ExternalLink, Loader2, Trash2 } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const router = useRouter()
const queryClient = useQueryClient()

const {
  data: savedSearches,
  isLoading,
  isError,
} = useQuery({
  queryKey: queryKeys.savedSearches(),
  queryFn: SavedSearchesService.listar,
})

const { mutate: removeSearch, isPending: isRemoving } = useMutation({
  mutationFn: (id: number) => SavedSearchesService.deletar(id),
  onSuccess: () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.savedSearches() })
  },
})

function openSearch(item: SavedSearchDTO) {
  router.push({ path: '/', query: { consulta: item.query } })
}

function formatUpdatedAt(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `Atualizada em ${date.toLocaleDateString('pt-BR')}`
}
</script>

<template>
  <section class="page-stack">
    <header>
      <h1>Buscas salvas</h1>
      <p>Retome pesquisas recentes e acompanhe os insights sem repetir a consulta.</p>
    </header>

    <EmptyPanel
      v-if="isLoading"
      title="Carregando suas buscas…"
      description="Buscando as consultas que você salvou."
    />

    <EmptyPanel
      v-else-if="isError"
      title="Não foi possível carregar"
      description="Tente novamente em instantes."
    />

    <div v-else-if="savedSearches && savedSearches.length" class="list">
      <BaseCard v-for="item in savedSearches" :key="item.id">
        <div class="item-head">
          <div>
            <h2>{{ item.title }}</h2>
            <p><Clock3 :size="14" /> {{ formatUpdatedAt(item.updated_at) }}</p>
          </div>
          <div class="actions">
            <button type="button" class="ghost" @click="openSearch(item)">
              <ExternalLink :size="15" /> Abrir
            </button>
            <button
              type="button"
              class="ghost danger"
              :disabled="isRemoving"
              @click="removeSearch(item.id)"
            >
              <Loader2 v-if="isRemoving" :size="15" class="spin" />
              <Trash2 v-else :size="15" />
              Remover
            </button>
          </div>
        </div>
        <p class="query">{{ item.query }}</p>
      </BaseCard>
    </div>

    <EmptyPanel
      v-else
      title="Nenhuma busca salva"
      description="Salve consultas importantes para acompanhar mudancas de jurisprudencia com rapidez."
    />
  </section>
</template>

<style scoped>
.page-stack {
  display: grid;
  gap: 0.95rem;
}

h1 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
}

header p {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
}

.list {
  display: grid;
  gap: 0.75rem;
}

.item-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

h2 {
  margin: 0;
  color: var(--brand-strong);
  font-size: 1.06rem;
}

.item-head p {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.query {
  margin: 0.8rem 0 0;
}

.actions {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.ghost {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 0.42rem 0.62rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: var(--bg-surface);
  color: var(--text-body);
  cursor: pointer;
}

.ghost:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.danger {
  color: #8a2334;
  border-color: #e7bcc5;
}

.spin {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 740px) {
  .item-head {
    flex-direction: column;
  }
}
</style>
