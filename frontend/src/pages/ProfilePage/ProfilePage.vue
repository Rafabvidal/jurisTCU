<script setup lang="ts">
import BaseCard from '@/shared/components/ui/BaseCard.vue'
import { useAuthStore } from '@/stores/auth'
import { BadgeCheck, Check, Edit2, Loader2, Mail, UserRound, X } from 'lucide-vue-next'
import { computed, ref } from 'vue'

const authStore = useAuthStore()

// Reactive form state
const isEditing = ref(false)
const newName = ref(authStore.user?.name || '')
const isLoading = ref(false)
const statusMessage = ref<{ type: 'success' | 'error'; text: string } | null>(null)

// Get current dynamic user name or fallback
const currentName = computed(() => authStore.user?.name || 'Usuário')
const currentEmail = computed(() => authStore.user?.email || 'email@example.com')
const userInitials = computed(() => authStore.initials)

function startEditing() {
  newName.value = authStore.user?.name || ''
  isEditing.value = true
  statusMessage.value = null
}

function cancelEditing() {
  isEditing.value = false
  statusMessage.value = null
}

async function saveProfile() {
  if (!newName.value.trim()) {
    statusMessage.value = { type: 'error', text: 'O nome não pode ficar em branco.' }
    return
  }

  isLoading.value = true
  statusMessage.value = null

  try {
    await authStore.updateProfile(newName.value.trim())
    isEditing.value = false
    statusMessage.value = { type: 'success', text: 'Perfil atualizado com sucesso!' }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (error: any) {
    statusMessage.value = {
      type: 'error',
      text: error?.response?.data?.detail || 'Erro ao salvar alterações. Tente novamente.',
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <section class="page-stack">
    <header>
      <h1>Perfil do usuário</h1>
      <p>Gestão de identidade e contexto profissional usado nas análises.</p>
    </header>

    <BaseCard class="profile-card">
      <div class="profile-head">
        <div class="avatar-wrapper">
          <div class="avatar" v-if="userInitials && userInitials !== '?'">
            {{ userInitials }}
          </div>
          <div class="avatar" v-else>
            <UserRound :size="24" />
          </div>
        </div>
        <div class="profile-title">
          <div class="name-badge-row">
            <h2>{{ currentName }}</h2>
            <span class="badge"><BadgeCheck :size="14" /> Conta ativa</span>
          </div>
          <p class="role-desc">Usuário cadastrado no sistema</p>
        </div>
      </div>

      <div class="divider"></div>

      <div class="info-section">
        <h3>Informações Pessoais</h3>
        <ul class="info-list">
          <li>
            <div class="info-icon"><Mail :size="16" /></div>
            <div class="info-content">
              <span class="info-label">E-mail de acesso</span>
              <span class="info-val">{{ currentEmail }}</span>
            </div>
          </li>
          
        </ul>
      </div>

      <div class="divider"></div>

      <!-- Profile Edit Section -->
      <div class="edit-section">
        <div v-if="!isEditing" class="display-actions">
          <button class="btn btn-secondary" @click="startEditing">
            <Edit2 :size="14" />
            Editar nome do perfil
          </button>
        </div>

        <form v-else @submit.prevent="saveProfile" class="edit-form">
          <div class="form-group">
            <label for="profile-name">Nome Completo</label>
            <div class="input-wrapper">
              <input
                id="profile-name"
                v-model="newName"
                type="text"
                class="form-control"
                placeholder="Insira seu nome"
                :disabled="isLoading"
                required
              />
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-ghost" @click="cancelEditing" :disabled="isLoading">
              <X :size="14" /> Cancelar
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-row">
                <Loader2 class="spinner" :size="14" /> Salvando...
              </span>
              <span v-else class="btn-row">
                <Check :size="14" /> Salvar alterações
              </span>
            </button>
          </div>
        </form>

        <Transition name="fade">
          <div v-if="statusMessage" :class="['alert', `alert-${statusMessage.type}`]">
            <span class="alert-text">{{ statusMessage.text }}</span>
          </div>
        </Transition>
      </div>
    </BaseCard>
  </section>
</template>

<style scoped>
.page-stack {
  display: grid;
  gap: 1.5rem;
  max-width: 680px;
  margin: 0 auto;
  padding: 1rem 0;
}

h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--text-strong);
  letter-spacing: -0.02em;
}

header p {
  margin: 0.4rem 0 0;
  font-size: 1.05rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.profile-card {
  padding: 2rem;
  border-radius: 20px;
  background: var(--bg-surface);
  border: 1px solid var(--line);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.profile-head {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  border: 2px solid var(--line);
  display: grid;
  place-items: center;
  font-size: 1.4rem;
  font-weight: 700;
  font-family: var(--font-display);
  color: var(--brand);
  background: var(--brand-soft);
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.avatar-wrapper:hover .avatar {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 102, 204, 0.15);
}

.profile-title {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.name-badge-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-strong);
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.6rem;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.role-desc {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted);
}

.divider {
  height: 1px;
  background: var(--line);
  margin: 1.5rem 0;
}

.info-section h3 {
  margin: 0 0 1rem;
  font-size: 0.95rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.info-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 1.2rem;
}

.info-list li {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.info-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--bg-hover);
  border: 1px solid var(--line);
  display: grid;
  place-items: center;
  color: var(--brand);
  flex-shrink: 0;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.info-val {
  font-size: 0.95rem;
  color: var(--text-strong);
  font-weight: 500;
  line-height: 1.4;
}

.edit-section {
  display: grid;
  gap: 1rem;
}

.display-actions {
  display: flex;
  justify-content: flex-end;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem 1.2rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-primary {
  background: var(--brand);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--brand-hover, #0056b3);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2);
}

.btn-secondary {
  background: var(--bg-hover);
  border-color: var(--line);
  color: var(--text-strong);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--line);
  transform: translateY(-1px);
}

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-strong);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.edit-form {
  display: grid;
  gap: 1.25rem;
  animation: slideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.form-group {
  display: grid;
  gap: 0.45rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-strong);
}

.input-wrapper {
  position: relative;
}

.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: var(--bg-input, #ffffff);
  color: var(--text-strong);
  font-size: 0.95rem;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.15);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.spinner-row,
.btn-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.spinner {
  animation: spin 1s linear infinite;
}

.alert {
  padding: 0.85rem 1.1rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  animation: fadeIn 0.3s ease;
}

.alert-success {
  background: rgba(16, 185, 129, 0.15);
  color: #065f46;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.alert-error {
  background: rgba(239, 68, 68, 0.15);
  color: #991b1b;
  border: 1px solid rgba(239, 68, 68, 0.25);
}

/* Animations */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
