import { useQuery } from '@tanstack/vue-query'
import { computed, type ComputedRef, type Ref } from 'vue'

import { MainService } from '@/services/MainService'
import { queryKeys } from '@/services/queryKeys'
import { DEFAULT_TOP_K } from '@/shared/constants/api'
import type { BuscaSemanticaResponse } from '@/shared/types/api'
import type { ProcessCase } from '@/shared/types/cases'
import { mapProcessoDTOToProcessCase } from '@/utils/mappers'

export interface UseBuscaSemanticaOptions {
  topK?: number
  metrica?: Ref<string>
}

export function useBuscaSemantica(
  consulta: Ref<string>,
  enabled: Ref<boolean> | ComputedRef<boolean>,
  options: UseBuscaSemanticaOptions = {},
) {
  const topK = options.topK ?? DEFAULT_TOP_K

  return useQuery<BuscaSemanticaResponse, Error, ProcessCase[]>({
    queryKey: computed(() => queryKeys.buscaSemantica(consulta.value, topK, options.metrica?.value)),
    queryFn: () =>
      MainService.buscaSemantica({
        consulta: consulta.value,
        top_k: topK,
        metrica: options.metrica?.value,
      }),
    enabled,
    select: (response) => response.items.map(mapProcessoDTOToProcessCase),
  })
}
