import api from "./api"

export interface SearchItem {
  id: string
  label: string
  description?: string
  /** Named icon key: "user" | "users" | "document" | "home" | "logout" | "sun" | "moon" | "monitor" */
  icon?: string
  /** Frontend route to navigate to when selected */
  url?: string
}

export interface SearchGroup {
  category: string
  items: SearchItem[]
}

export interface SearchResponse {
  query: string
  groups: SearchGroup[]
}

export const searchService = {
  async search(query: string, limit = 5): Promise<SearchResponse> {
    const { data } = await api.get<SearchResponse>("/search/", {
      params: { q: query, limit },
    })
    return data
  },
}
