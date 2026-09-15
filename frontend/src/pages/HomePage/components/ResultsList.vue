<script setup lang="ts">
import { queryKeys } from '@/services/queryKeys'
import { SavedSearchesService } from '@/services/savedSearchesService'
import { useAuthStore } from '@/stores/auth'
import type { ProcessCase } from '@/shared/types/cases'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { Bookmark, Check, Loader2, LogIn, X } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import ResultCard from './ResultCard.vue'

const props = defineProps<{ items: ProcessCase[]; query: string }>()

const authStore = useAuthStore()
const router = useRouter()
const queryClient = useQueryClient()

type ModalMode = 'save' | 'login' | null
const modalMode = ref<ModalMode>(null)
const titleInput = ref('')
const justSaved = ref(false)

function suggestTitle(query: string): string {
  return query.trim().split(/\s+/).slice(0, 6).join(' ')
}

function openSaveModal() {
  justSaved.value = false
  if (!authStore.isAuthenticated) {
    modalMode.value = 'login'
    return
  }
  titleInput.value = suggestTitle(props.query)
  modalMode.value = 'save'
}

function closeModal() {
  modalMode.value = null
}

function goToLogin() {
  closeModal()
  router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
}

const { mutate: saveSearch, isPending: isSaving, isError: saveFailed } = useMutation({
  mutationFn: () => SavedSearchesService.criar(titleInput.value.trim(), props.query),
  onSuccess: () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.savedSearches() })
    justSaved.value = true
    setTimeout(closeModal, 900)
  },
})

const canSave = computed(() => Boolean(titleInput.value.trim()) && !isSaving.value)
</script>

<template>
  <section class="results-list">
    <header>
      <div class="head-text">
        <h2>Resultados encontrados ({{ items.length }})</h2>
        <p>Casos semanticamente próximos para o seu contexto, ordenados por similaridade.</p>
      </div>
      <button type="button" class="save-btn" @click="openSaveModal">
        <Bookmark :size="15" />
        <span>Salvar busca</span>
      </button>
    </header>

    <div
      v-for="(item, idx) in items"
      :key="item.numeroProcesso"
      v-motion
      :initial="{ opacity: 0, y: 16 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: idx * 70 } }"
    >
      <ResultCard :item="item" />
    </div>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modalMode" class="modal-overlay" @click.self="closeModal">
          <div
            class="modal"
            role="dialog"
            aria-modal="true"
            v-motion
            :initial="{ opacity: 0, scale: 0.96, y: 8 }"
            :enter="{ opacity: 1, scale: 1, y: 0 }"
          >
            <button type="button" class="close" aria-label="Fechar" @click="closeModal">
              <X :size="18" />
            </button>

            <template v-if="modalMode === 'save'">
              <h3>Salvar esta busca</h3>
              <p class="modal-sub">Dê um nome amigável para encontrá-la depois.</p>

              <label class="field">
                <span>Título</span>
                <input
                  v-model="titleInput"
                  type="text"
                  maxlength="150"
                  placeholder="Ex.: Escala 12x36 sem intervalo"
                  @keyup.enter="canSave && saveSearch()"
                />
              </label>

              <p class="query-preview">{{ query }}</p>

              <p v-if="saveFailed" class="alert" role="alert">
                Não foi possível salvar. Tente novamente.
              </p>

              <div class="modal-actions">
                <button type="button" class="ghost" @click="closeModal">Cancelar</button>
                <button type="button" class="primary" :disabled="!canSave" @click="saveSearch()">
                  <Check v-if="justSaved" :size="16" />
                  <Loader2 v-else-if="isSaving" :size="16" class="spin" />
                  <span>{{ justSaved ? 'Salva!' : 'Salvar' }}</span>
                </button>
              </div>
            </template>

            <template v-else>
              <h3>Salve suas pesquisas</h3>
              <p class="modal-sub">
                Entre na sua conta para guardar esta busca e retomá-la quando quiser.
              </p>
              <div class="modal-actions">
                <button type="button" class="ghost" @click="closeModal">Agora não</button>
                <button type="button" class="primary" @click="goToLogin">
                  <LogIn :size="16" />
                  <span>Entrar</span>
                </button>
              </div>
            </template>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<style scoped>
.results-list {
  display: grid;
  gap: 0.8rem;
}

header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.2rem;
}

h2 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
  letter-spacing: -0.02em;
}

.head-text p {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
}

.save-btn {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.8rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  color: var(--brand-strong);
  font-weight: 600;
  font-size: 0.86rem;
  cursor: pointer;
  transition: all 200ms ease;
}

.save-btn:hover {
  background: var(--brand-soft);
  border-color: var(--brand-soft);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: grid;
  place-items: center;
  padding: 1.2rem;
  background: rgba(11, 22, 44, 0.45);
  backdrop-filter: blur(3px);
}

.modal {
  position: relative;
  width: min(440px, 100%);
  padding: 1.6rem;
  background: #f6f9ff;
  border: 1px solid #dde3eb;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.close {
  position: absolute;
  top: 0.9rem;
  right: 0.9rem;
  display: grid;
  place-items: center;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.modal h3 {
  margin: 0;
  font-family: var(--font-display);
  color: #002045;
}

.modal-sub {
  margin: 0.35rem 0 1.1rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.field {
  display: grid;
  gap: 0.3rem;
}

.field > span {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-body);
}

.field input {
  padding: 0.62rem 0.7rem;
  border: 1px solid #dde3eb;
  border-radius: var(--radius-sm);
  background: #ffffff;
  font: inherit;
  color: var(--text-strong);
  outline: none;
  transition: border-color 200ms ease, box-shadow 200ms ease;
}

.field input:focus {
  border-color: #002045;
  box-shadow: 0 0 0 3px rgba(0, 32, 69, 0.1);
}

.query-preview {
  margin: 0.7rem 0 0;
  padding: 0.55rem 0.7rem;
  background: #ffffff;
  border: 1px dashed #dde3eb;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-size: 0.85rem;
}

.alert {
  margin: 0.7rem 0 0;
  color: #8a2334;
  font-size: 0.85rem;
}

.modal-actions {
  margin-top: 1.2rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

.ghost,
.primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 0.9rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 180ms ease;
}

.ghost {
  border: 1px solid var(--line);
  background: var(--bg-surface);
  color: var(--text-body);
}

.primary {
  border: none;
  background: #002045;
  color: #ffffff;
}

.primary:hover:not(:disabled) {
  background: #00132b;
}

.primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.spin {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 200ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@media (max-width: 560px) {
  header {
    flex-direction: column;
  }
}
</style>
