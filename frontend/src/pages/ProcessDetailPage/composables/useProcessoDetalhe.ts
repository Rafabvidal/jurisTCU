import { useQuery } from '@tanstack/vue-query'
import type { ComputedRef, Ref } from 'vue'
import { computed } from 'vue'

import { MainService } from '@/services/MainService'
import { queryKeys } from '@/services/queryKeys'
import type { ProcessoDetalheDTO } from '@/shared/types/api'

export function useProcessoDetalhe(
  numeroProcesso: Ref<string> | ComputedRef<string>,
  grau: Ref<string> | ComputedRef<string>,
  enabled: Ref<boolean> | ComputedRef<boolean> = computed(
    () => Boolean(numeroProcesso.value && grau.value),
  ),
) {
  return useQuery<ProcessoDetalheDTO, Error>({
    queryKey: computed(() => queryKeys.processoDetalhe(numeroProcesso.value, grau.value)),
    queryFn: () => MainService.obterProcessoDetalhe(numeroProcesso.value, grau.value),
    enabled,
  })
}