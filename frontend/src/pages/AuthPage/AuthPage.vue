<script setup lang="ts">
import { HttpError } from '@/services/httpClient'
import { useAuthStore } from '@/stores/auth'
import { AtSign, Loader2, Lock, UserRound } from 'lucide-vue-next'
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

type Tab = 'login' | 'register'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeTab = ref<Tab>('login')
const isSubmitting = ref(false)
const formError = ref<string | null>(null)

const form = reactive({
  name: '',
  email: '',
  password: '',
})

const isLogin = computed(() => activeTab.value === 'login')

function switchTab(tab: Tab) {
  if (tab === activeTab.value) return
  activeTab.value = tab
  formError.value = null
}

const emailError = computed(() => {
  if (!form.email) return null
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) ? null : 'Informe um e-mail válido.'
})

const passwordError = computed(() => {
  if (!form.password) return null
  return form.password.length >= 8 ? null : 'A senha deve ter ao menos 8 caracteres.'
})

const canSubmit = computed(() => {
  if (isSubmitting.value) return false
  if (!form.email || !form.password) return false
  if (emailError.value || passwordError.value) return false
  if (!isLogin.value && !form.name.trim()) return false
  return true
})

async function handleSubmit() {
  if (!canSubmit.value) return
  formError.value = null
  isSubmitting.value = true

  try {
    if (isLogin.value) {
      await authStore.login(form.email, form.password)
    } else {
      await authStore.register(form.name.trim(), form.email, form.password)
    }
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await router.push(redirect)
  } catch (error) {
    formError.value =
      error instanceof HttpError
        ? error.message
        : 'Não foi possível concluir. Tente novamente.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <div
      class="auth-card"
      v-motion
      :initial="{ opacity: 0, y: 18 }"
      :enter="{ opacity: 1, y: 0 }"
    >
      <header class="auth-head">
        <h1>JusTRT6</h1>
        <p>{{ isLogin ? 'Bem-vindo de volta.' : 'Crie sua conta para salvar buscas.' }}</p>
      </header>

      <div class="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          :aria-selected="isLogin"
          :class="{ active: isLogin }"
          @click="switchTab('login')"
        >
          Entrar
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="!isLogin"
          :class="{ active: !isLogin }"
          @click="switchTab('register')"
        >
          Criar conta
        </button>
        <span class="tab-indicator" :class="{ right: !isLogin }" aria-hidden="true" />
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <Transition name="field">
          <label v-if="!isLogin" class="field">
            <span>Nome</span>
            <div class="control">
              <UserRound :size="16" />
              <input
                v-model="form.name"
                type="text"
                autocomplete="name"
                placeholder="Como devemos te chamar?"
              />
            </div>
          </label>
        </Transition>

        <label class="field">
          <span>E-mail</span>
          <div class="control" :class="{ invalid: emailError }">
            <AtSign :size="16" />
            <input
              v-model="form.email"
              type="email"
              autocomplete="email"
              placeholder="voce@exemplo.com"
            />
          </div>
          <small v-if="emailError" class="hint">{{ emailError }}</small>
        </label>

        <label class="field">
          <span>Senha</span>
          <div class="control" :class="{ invalid: passwordError }">
            <Lock :size="16" />
            <input
              v-model="form.password"
              type="password"
              :autocomplete="isLogin ? 'current-password' : 'new-password'"
              placeholder="••••••••"
            />
          </div>
          <small v-if="passwordError" class="hint">{{ passwordError }}</small>
        </label>

        <Transition name="field">
          <p v-if="formError" class="alert" role="alert">{{ formError }}</p>
        </Transition>

        <button type="submit" class="submit" :disabled="!canSubmit">
          <Loader2 v-if="isSubmitting" :size="16" class="spin" />
          <span>{{ isLogin ? 'Entrar' : 'Criar conta' }}</span>
        </button>
      </form>

      <footer class="auth-foot">
        <template v-if="isLogin">
          Ainda não tem conta?
          <button type="button" @click="switchTab('register')">Cadastre-se</button>
        </template>
        <template v-else>
          Já possui conta?
          <button type="button" @click="switchTab('login')">Entrar</button>
        </template>
      </footer>
    </div>
  </section>
</template>

<style scoped>
.auth-page {
  display: grid;
  place-items: center;
  min-height: 70vh;
  padding: 1.5rem;
}

.auth-card {
  width: min(420px, 100%);
  padding: 1.8rem;
  background: #f6f9ff;
  border: 1px solid #dde3eb;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.auth-head h1 {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #002045;
}

.auth-head p {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
}

.tabs {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin: 1.4rem 0 1.2rem;
  background: #ffffff;
  border: 1px solid #dde3eb;
  border-radius: var(--radius-sm);
  padding: 0.25rem;
}

.tabs button {
  position: relative;
  z-index: 1;
  border: none;
  background: transparent;
  padding: 0.55rem 0;
  font-weight: 600;
  font-size: 0.92rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 220ms ease;
}

.tabs button.active {
  color: #002045;
}

.tab-indicator {
  position: absolute;
  z-index: 0;
  top: 0.25rem;
  bottom: 0.25rem;
  left: 0.25rem;
  width: calc(50% - 0.25rem);
  background: #dbe7ff;
  border-radius: calc(var(--radius-sm) - 4px);
  transition: transform 260ms cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-indicator.right {
  transform: translateX(100%);
}

.auth-form {
  display: grid;
  gap: 0.85rem;
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

.control {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0 0.7rem;
  background: #ffffff;
  border: 1px solid #dde3eb;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  transition: border-color 200ms ease, box-shadow 200ms ease;
}

.control:focus-within {
  border-color: #002045;
  box-shadow: 0 0 0 3px rgba(0, 32, 69, 0.1);
}

.control.invalid {
  border-color: #c2384a;
}

.control input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 0.62rem 0;
  font: inherit;
  color: var(--text-strong);
}

.hint {
  color: #c2384a;
  font-size: 0.78rem;
}

.alert {
  margin: 0;
  padding: 0.6rem 0.75rem;
  background: #fdecef;
  border: 1px solid #f1c2cb;
  border-radius: var(--radius-sm);
  color: #8a2334;
  font-size: 0.85rem;
}

.submit {
  margin-top: 0.3rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem 1rem;
  border: none;
  border-radius: var(--radius-sm);
  background: #002045;
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  transition: background 200ms ease, transform 120ms ease, opacity 200ms ease;
}

.submit:hover:not(:disabled) {
  background: #00132b;
}

.submit:active:not(:disabled) {
  transform: translateY(1px);
}

.submit:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.auth-foot {
  margin-top: 1.1rem;
  text-align: center;
  font-size: 0.88rem;
  color: var(--text-muted);
}

.auth-foot button {
  border: none;
  background: transparent;
  color: #002045;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.spin {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.field-enter-active,
.field-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.field-enter-from,
.field-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
