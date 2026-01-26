import api from "./api"

export interface User {
  id: string
  name: string
  surname: string | null
  email: string
  phone_number: string
  avatar_url: string | null
  role: string
  extra_data: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface LoginPayload {
  identifier: string
  password: string
}

export interface RegisterPayload {
  name: string
  surname?: string
  email: string
  phone_number: string
  password: string
}

export interface UpdateProfilePayload {
  name?: string
  surname?: string | null
  phone_number?: string
}

export interface ChangePasswordPayload {
  current_password: string
  new_password: string
}

interface TokenResponse {
  access_token: string
  token_type: string
}

export const authService = {
  async login(payload: LoginPayload): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/login", payload)
    return data
  },

  async register(payload: RegisterPayload): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/register", payload)
    return data
  },

  async getMe(): Promise<User> {
    const { data } = await api.get<User>("/users/me")
    return data
  },

  async updateProfile(payload: UpdateProfilePayload): Promise<User> {
    const { data } = await api.put<User>("/users/me", payload)
    return data
  },

  async uploadAvatar(file: File): Promise<User> {
    const formData = new FormData()
    formData.append("file", file)
    const { data } = await api.post<User>("/users/me/avatar", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    return data
  },

  async changePassword(payload: ChangePasswordPayload): Promise<void> {
    await api.put("/users/me/password", payload)
  },

  async logout(): Promise<void> {
    await api.post("/auth/logout")
  },
}
