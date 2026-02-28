import { computed, ref } from "vue"
import { defineStore } from "pinia"
import {
  authService,
  type ConnectFacebookPayload,
  type ConnectGooglePayload,
  type LoginPayload,
  type RegisterPayload,
  type UpdateProfilePayload,
  type User,
} from "@/services/auth"

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem("token"))

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  async function login(payload: LoginPayload) {
    const response = await authService.login(payload)
    token.value = response.access_token
    localStorage.setItem("token", response.access_token)
    await fetchUser()
  }

  async function register(payload: RegisterPayload) {
    const response = await authService.register(payload)
    token.value = response.access_token
    localStorage.setItem("token", response.access_token)
    await fetchUser()
  }

  async function loginWithGoogle(credential: string) {
    const response = await authService.googleAuth({ credential, is_signup: false })
    token.value = response.access_token
    localStorage.setItem("token", response.access_token)
    await fetchUser()
  }

  async function signupWithGoogle(credential: string) {
    const response = await authService.googleAuth({ credential, is_signup: true })
    token.value = response.access_token
    localStorage.setItem("token", response.access_token)
    await fetchUser()
  }

  async function loginWithFacebook(accessToken: string) {
    const response = await authService.facebookAuth({ access_token: accessToken, is_signup: false })
    token.value = response.access_token
    localStorage.setItem("token", response.access_token)
    await fetchUser()
  }

  async function signupWithFacebook(accessToken: string) {
    const response = await authService.facebookAuth({ access_token: accessToken, is_signup: true })
    token.value = response.access_token
    localStorage.setItem("token", response.access_token)
    await fetchUser()
  }

  async function fetchUser() {
    try {
      user.value = await authService.getMe()
    } catch {
      logout()
    }
  }

  async function updateProfile(payload: UpdateProfilePayload) {
    user.value = await authService.updateProfile(payload)
  }

  async function uploadAvatar(file: File) {
    user.value = await authService.uploadAvatar(file)
  }

  async function connectGoogle(payload: ConnectGooglePayload) {
    user.value = await authService.connectGoogle(payload)
  }

  async function disconnectGoogle() {
    user.value = await authService.disconnectGoogle()
  }

  async function connectFacebook(payload: ConnectFacebookPayload) {
    user.value = await authService.connectFacebook(payload)
  }

  async function disconnectFacebook() {
    user.value = await authService.disconnectFacebook()
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem("token")
  }

  return { 
    user, token, isAuthenticated, login, register, loginWithGoogle, loginWithFacebook, signupWithGoogle, signupWithFacebook, 
    fetchUser, updateProfile, uploadAvatar, logout, connectGoogle, disconnectGoogle, connectFacebook, disconnectFacebook, }
})
