import { API_ENDPOINTS } from '@/shared/constants/api'
import type { PaginatedResponse, SavedSearchDTO } from '@/shared/types/api'

import { httpClient } from './httpClient'

export class SavedSearchesService {
  static async listar(): Promise<SavedSearchDTO[]> {
    const { data } = await httpClient.get<PaginatedResponse<SavedSearchDTO>>(
      API_ENDPOINTS.savedSearches,
    )
    return data.results
  }

  static async criar(title: string, query: string): Promise<SavedSearchDTO> {
    const { data } = await httpClient.post<SavedSearchDTO>(API_ENDPOINTS.savedSearches, {
      title,
      query,
    })
    return data
  }

  static async deletar(id: number): Promise<void> {
    await httpClient.delete(`${API_ENDPOINTS.savedSearches}${id}/`)
  }
}
