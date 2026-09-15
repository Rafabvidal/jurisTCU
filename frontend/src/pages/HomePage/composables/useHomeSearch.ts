import { storeToRefs } from 'pinia'
import { computed, ref } from 'vue'

import { useBuscaSemantica } from '@/composables/useBuscaSemantica'
import { useSettingsStore } from '@/stores/settings'

import { useHomeInsights } from './useHomeInsights'

export function useHomeSearch() {
  const settingsStore = useSettingsStore()
  const { metrica } = storeToRefs(settingsStore)

  const query = ref('')
  const hasSearched = ref(false)
  const submittedQuery = ref('')

  const enabled = computed(
    () => hasSearched.value && submittedQuery.value.trim().length > 0,
  )

  const {
    data: cases,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
  } = useBuscaSemantica(submittedQuery, enabled, { metrica })

  const insights = useHomeInsights(cases)

  function submitSearch(value: string) {
    const trimmed = value.trim()
    if (!trimmed) return
    query.value = trimmed
    submittedQuery.value = trimmed
    hasSearched.value = true
  }

  return {
    query,
    metrica,
    hasSearched,
    submitSearch,
    cases,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
    insights,
  }
}

