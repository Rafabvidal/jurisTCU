import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const metrica = ref<string>(localStorage.getItem('pref_metrica') || 'cosseno')
  const language = ref<string>(localStorage.getItem('pref_language') || 'pt-BR')
  const notifications = ref<boolean>(
    localStorage.getItem('pref_notifications') !== 'false'
  )
  const highContrast = ref<boolean>(
    localStorage.getItem('pref_highContrast') === 'true'
  )

  watch(metrica, (val) => localStorage.setItem('pref_metrica', val))
  watch(language, (val) => localStorage.setItem('pref_language', val))
  watch(notifications, (val) => localStorage.setItem('pref_notifications', String(val)))
  watch(highContrast, (val) => localStorage.setItem('pref_highContrast', String(val)))

  return {
    metrica,
    language,
    notifications,
    highContrast,
  }
})
