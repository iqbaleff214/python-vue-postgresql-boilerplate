import api from "./api"

export interface User {
  id: string
  name: string
  surname: string | null
  email: string
  phone_number: string | null
  avatar_url: string | null
  role: string
  extra_data: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface GoogleAuthPayload {
  credential: string
  is_signup: boolean
}

export interface FacebookAuthPayload {
  access_token: string
  is_signup: boolean
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

export interface ForgotPasswordPayload {
  email: string
}

export interface ResetPasswordPayload {
  token: string
  new_password: string
}

export interface ConnectGooglePayload {
  credential: string
}

export interface ConnectFacebookPayload {
  access_token: string
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

  async googleAuth(payload: GoogleAuthPayload): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/google", payload)
    return data
  },

  async facebookAuth(payload: FacebookAuthPayload): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/facebook", payload)
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

  async forgotPassword(payload: ForgotPasswordPayload): Promise<{ message: string }> {
    const { data } = await api.post<{ message: string }>("/auth/forgot-password", payload)
    return data
  },

  async resetPassword(payload: ResetPasswordPayload): Promise<{ message: string }> {
    const { data } = await api.post<{ message: string }>("/auth/reset-password", payload)
    return data
  },
  
  async connectGoogle(payload: ConnectGooglePayload): Promise<User> {
    const { data } = await api.post<User>("/users/me/connect/google", payload)
    return data
  },

  async disconnectGoogle(): Promise<User> {
    const { data } = await api.delete<User>("/users/me/connect/google")
    return data
  },

  async connectFacebook(payload: ConnectFacebookPayload): Promise<User> {
    const { data } = await api.post<User>("/users/me/connect/facebook", payload)
    return data
  },

  async disconnectFacebook(): Promise<User> {
    const { data } = await api.delete<User>("/users/me/connect/facebook")
    return data
  },
}
