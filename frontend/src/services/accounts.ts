import api from "./api"
import type { User } from "./auth"

export interface CreateAccountPayload {
  name: string
  surname?: string
  email: string
  phone_number: string
  password: string
  role: "ADMIN" | "STAFF" | "USER"
}

export const accountsService = {
  async list(): Promise<User[]> {
    const { data } = await api.get<User[]>("/accounts/")
    return data
  },

  async get(id: string): Promise<User> {
    const { data } = await api.get<User>(`/accounts/${id}`)
    return data
  },

  async create(payload: CreateAccountPayload): Promise<User> {
    const { data } = await api.post<User>("/accounts/", payload)
    return data
  },

  async remove(id: string): Promise<void> {
    await api.delete(`/accounts/${id}`)
  },
}
