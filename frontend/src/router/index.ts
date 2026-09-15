import AuthPage from '@/pages/AuthPage/AuthPage.vue'
import HomePage from '@/pages/HomePage/HomePage.vue'
import ProcessDetailPage from '@/pages/ProcessDetailPage/ProcessDetailPage.vue'
import ProfilePage from '@/pages/ProfilePage/ProfilePage.vue'
import SavedSearchesPage from '@/pages/SavedSearchesPage/SavedSearchesPage.vue'
import SettingsPage from '@/pages/SettingsPage/SettingsPage.vue'
import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomePage },
    { path: '/login', component: AuthPage, meta: { guestOnly: true } },
    { path: '/processos/:numeroProcesso/:grau', component: ProcessDetailPage },
    { path: '/buscas-salvas', component: SavedSearchesPage, meta: { requiresAuth: true } },
    { path: '/perfil', component: ProfilePage, meta: { requiresAuth: true } },
    { path: '/configuracoes', component: SettingsPage },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // Usuário já logado não precisa ver a página de login/cadastro.
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { path: '/' }
  }

  return true
})

export default router
