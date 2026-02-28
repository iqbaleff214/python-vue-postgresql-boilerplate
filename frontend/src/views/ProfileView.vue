<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import AppLayout from "@/components/AppLayout.vue"
import UserAvatar from "@/components/UserAvatar.vue"
import { useAuthStore } from "@/stores/auth"
import { authService } from "@/services/auth"

declare const google: any
declare const FB: any

const auth = useAuthStore()

const name = ref("")
const surname = ref("")
const phoneNumber = ref("")
const saving = ref(false)
const success = ref("")
const error = ref("")

const avatarUploading = ref(false)
const avatarPreview = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const currentPassword = ref("")
const newPassword = ref("")
const confirmPassword = ref("")
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const changingPassword = ref(false)
const passwordSuccess = ref("")
const passwordError = ref("")

const socialError = ref("")
const socialSuccess = ref("")
const connectingGoogle = ref(false)
const connectingFacebook = ref(false)

const hasGoogle = computed(() => !!auth.user?.extra_data?.google_id)
const hasFacebook = computed(() => !!auth.user?.extra_data?.facebook_id)

onMounted(() => {
  if (auth.user) {
    name.value = auth.user.name
    surname.value = auth.user.surname || ""
    phoneNumber.value = auth.user.phone_number
  }
  if (typeof FB !== "undefined") {
    FB.init({
      appId: import.meta.env.VITE_FACEBOOK_APP_ID,
      cookie: true,
      xfbml: false,
      version: "v22.0",
    })
  }
})

async function handleSave() {
  error.value = ""
  success.value = ""
  saving.value = true
  try {
    await auth.updateProfile({
      name: name.value,
      surname: surname.value || undefined,
      phone_number: phoneNumber.value,
    })
    success.value = "Profile updated successfully."
  } catch (err: any) {
    error.value = err.response?.data?.detail || "Failed to update profile."
  } finally {
    saving.value = false
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}

async function handleAvatarChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  error.value = ""
  success.value = ""

  const allowed = ["image/jpeg", "image/png", "image/webp", "image/gif"]
  if (!allowed.includes(file.type)) {
    error.value = "File must be JPEG, PNG, WebP, or GIF."
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    error.value = "File size must not exceed 5 MB."
    return
  }

  avatarPreview.value = URL.createObjectURL(file)
  avatarUploading.value = true
  try {
    await auth.uploadAvatar(file)
    avatarPreview.value = null
    success.value = "Avatar updated successfully."
  } catch (err: any) {
    avatarPreview.value = null
    error.value = err.response?.data?.detail || "Failed to upload avatar."
  } finally {
    avatarUploading.value = false
    target.value = ""
  }
}

async function handleChangePassword() {
  passwordError.value = ""
  passwordSuccess.value = ""

  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = "New passwords do not match."
    return
  }

  changingPassword.value = true
  try {
    await authService.changePassword({
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })
    passwordSuccess.value = "Password changed successfully."
    currentPassword.value = ""
    newPassword.value = ""
    confirmPassword.value = ""
  } catch (err: any) {
    passwordError.value =
      err.response?.data?.detail || "Failed to change password."
  } finally {
    changingPassword.value = false
  }
}

async function handleConnectGoogle() {
  socialError.value = ""
  socialSuccess.value = ""
  google.accounts.id.initialize({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    callback: async ({ credential }: { credential: string }) => {
      connectingGoogle.value = true
      try {
        await auth.connectGoogle({ credential })
        socialSuccess.value = "Google account connected successfully."
      } catch (err: any) {
        socialError.value = err.response?.data?.detail || "Failed to connect Google account."
      } finally {
        connectingGoogle.value = false
      }
    },
  })
  google.accounts.id.prompt()
}

async function handleDisconnectGoogle() {
  socialError.value = ""
  socialSuccess.value = ""
  connectingGoogle.value = true
  try {
    await auth.disconnectGoogle()
    socialSuccess.value = "Google account disconnected."
  } catch (err: any) {
    socialError.value = err.response?.data?.detail || "Failed to disconnect Google account."
  } finally {
    connectingGoogle.value = false
  }
}

async function handleConnectFacebook() {
  socialError.value = ""
  socialSuccess.value = ""
  FB.login(
    async (res: any) => {
      if (res.authResponse) {
        connectingFacebook.value = true
        try {
          await auth.connectFacebook({ access_token: res.authResponse.accessToken })
          socialSuccess.value = "Facebook account connected successfully."
        } catch (err: any) {
          socialError.value = err.response?.data?.detail || "Failed to connect Facebook account."
        } finally {
          connectingFacebook.value = false
        }
      }
    },
    { scope: "public_profile,email" },
  )
}

async function handleDisconnectFacebook() {
  socialError.value = ""
  socialSuccess.value = ""
  connectingFacebook.value = true
  try {
    await auth.disconnectFacebook()
    socialSuccess.value = "Facebook account disconnected."
  } catch (err: any) {
    socialError.value = err.response?.data?.detail || "Failed to disconnect Facebook account."
  } finally {
    connectingFacebook.value = false
  }
}
</script>

<template>
  <AppLayout>
    <div class="space-y-4">
      <!-- Page Header -->
      <div>
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">Profile</h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Manage your personal information and account settings.
        </p>
      </div>

      <!-- Two-column grid: left sidebar + right forms -->
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">

        <!-- Left column: Avatar + Connected Accounts -->
        <div class="space-y-4">

          <!-- Avatar card -->
          <div class="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
            <h2 class="mb-3 text-sm font-semibold text-gray-900 dark:text-white">Avatar</h2>

            <!-- Avatar feedback -->
            <div
              v-if="success"
              class="mb-3 rounded-lg bg-green-50 p-2.5 text-xs text-green-700 dark:bg-green-900/20 dark:text-green-400"
            >
              {{ success }}
            </div>
            <div
              v-if="error"
              class="mb-3 rounded-lg bg-red-50 p-2.5 text-xs text-red-600 dark:bg-red-900/20 dark:text-red-400"
            >
              {{ error }}
            </div>

            <div class="flex flex-col items-center gap-3 text-center">
              <div class="relative">
                <UserAvatar
                  :name="auth.user?.name ?? ''"
                  :avatar-url="avatarPreview || auth.user?.avatar_url"
                  size="lg"
                />
                <div
                  v-if="avatarUploading"
                  class="absolute inset-0 flex items-center justify-center rounded-full bg-black/40"
                >
                  <svg class="h-5 w-5 animate-spin text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                </div>
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ auth.user?.name }} {{ auth.user?.surname }}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ auth.user?.email }}</p>
                <span class="mt-1 inline-block rounded-full bg-violet-100 px-2 py-0.5 text-xs font-medium text-violet-700 dark:bg-violet-900/30 dark:text-violet-400">
                  {{ auth.user?.role }}
                </span>
              </div>
              <div class="w-full border-t border-gray-100 pt-3 dark:border-gray-800">
                <button
                  type="button"
                  :disabled="avatarUploading"
                  class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                  @click="triggerFileInput"
                >
                  {{ avatarUploading ? "Uploading..." : "Change avatar" }}
                </button>
                <p class="mt-1.5 text-xs text-gray-400 dark:text-gray-500">
                  JPEG, PNG, WebP or GIF · Max 5 MB
                </p>
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/jpeg,image/png,image/webp,image/gif"
                  class="hidden"
                  @change="handleAvatarChange"
                />
              </div>
            </div>
          </div>

          <!-- Connected Accounts -->
          <div class="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
            <h2 class="mb-1 text-sm font-semibold text-gray-900 dark:text-white">Connected Accounts</h2>
            <p class="mb-3 text-xs text-gray-500 dark:text-gray-400">
              Sign in faster using a linked social account.
            </p>

            <!-- Social feedback -->
            <div
              v-if="socialSuccess"
              class="mb-3 rounded-lg bg-green-50 p-2.5 text-xs text-green-700 dark:bg-green-900/20 dark:text-green-400"
            >
              {{ socialSuccess }}
            </div>
            <div
              v-if="socialError"
              class="mb-3 rounded-lg bg-red-50 p-2.5 text-xs text-red-600 dark:bg-red-900/20 dark:text-red-400"
            >
              {{ socialError }}
            </div>

            <div class="space-y-2">
              <!-- Google -->
              <div class="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 px-3 py-2.5 dark:border-gray-700 dark:bg-gray-800">
                <div class="flex items-center gap-2.5">
                  <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  <div>
                    <p class="text-xs font-medium text-gray-900 dark:text-white">Google</p>
                    <p class="text-xs text-gray-400 dark:text-gray-500">
                      {{ hasGoogle ? "Connected" : "Not connected" }}
                    </p>
                  </div>
                </div>
                <button
                  v-if="!hasGoogle"
                  type="button"
                  :disabled="connectingGoogle"
                  class="rounded border border-gray-300 bg-white px-2.5 py-1 text-xs font-medium text-gray-600 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300"
                  @click="handleConnectGoogle"
                >
                  {{ connectingGoogle ? "..." : "Connect" }}
                </button>
                <button
                  v-else
                  type="button"
                  :disabled="connectingGoogle"
                  class="rounded border border-red-200 bg-white px-2.5 py-1 text-xs font-medium text-red-600 transition hover:bg-red-50 disabled:opacity-50 dark:border-red-800 dark:bg-gray-700 dark:text-red-400"
                  @click="handleDisconnectGoogle"
                >
                  {{ connectingGoogle ? "..." : "Disconnect" }}
                </button>
              </div>

              <!-- Facebook -->
              <div class="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 px-3 py-2.5 dark:border-gray-700 dark:bg-gray-800">
                <div class="flex items-center gap-2.5">
                  <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="#1877F2">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  <div>
                    <p class="text-xs font-medium text-gray-900 dark:text-white">Facebook</p>
                    <p class="text-xs text-gray-400 dark:text-gray-500">
                      {{ hasFacebook ? "Connected" : "Not connected" }}
                    </p>
                  </div>
                </div>
                <button
                  v-if="!hasFacebook"
                  type="button"
                  :disabled="connectingFacebook"
                  class="rounded border border-gray-300 bg-white px-2.5 py-1 text-xs font-medium text-gray-600 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300"
                  @click="handleConnectFacebook"
                >
                  {{ connectingFacebook ? "..." : "Connect" }}
                </button>
                <button
                  v-else
                  type="button"
                  :disabled="connectingFacebook"
                  class="rounded border border-red-200 bg-white px-2.5 py-1 text-xs font-medium text-red-600 transition hover:bg-red-50 disabled:opacity-50 dark:border-red-800 dark:bg-gray-700 dark:text-red-400"
                  @click="handleDisconnectFacebook"
                >
                  {{ connectingFacebook ? "..." : "Disconnect" }}
                </button>
              </div>
            </div>
          </div>

        </div>

        <!-- Right column (spans 2): Personal Info + Change Password -->
        <div class="space-y-4 lg:col-span-2">

          <!-- Personal Information -->
          <form
            class="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
            @submit.prevent="handleSave"
          >
            <h2 class="mb-3 text-sm font-semibold text-gray-900 dark:text-white">Personal Information</h2>

            <div class="space-y-3">
              <!-- Name + Surname -->
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label for="profile-name" class="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
                    First name
                  </label>
                  <input
                    id="profile-name"
                    v-model="name"
                    type="text"
                    required
                    class="w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
                  />
                </div>
                <div>
                  <label for="profile-surname" class="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
                    Last name
                  </label>
                  <input
                    id="profile-surname"
                    v-model="surname"
                    type="text"
                    class="w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
                  />
                </div>
              </div>

              <!-- Email + Phone on same row -->
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label for="profile-email" class="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
                    Email
                  </label>
                  <input
                    id="profile-email"
                    :value="auth.user?.email"
                    type="email"
                    disabled
                    class="w-full rounded-lg border border-gray-200 bg-gray-100 px-3 py-2 text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-400"
                  />
                  <p class="mt-1 text-xs text-gray-400 dark:text-gray-500">Cannot be changed.</p>
                </div>
                <div>
                  <label for="profile-phone" class="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
                    Phone number
                  </label>
                  <input
                    id="profile-phone"
                    v-model="phoneNumber"
                    type="tel"
                    required
                    class="w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
                  />
                </div>
              </div>
            </div>

            <div class="mt-4 flex items-center justify-end gap-3">
              <p v-if="success" class="text-xs text-green-600 dark:text-green-400">{{ success }}</p>
              <p v-if="error" class="text-xs text-red-600 dark:text-red-400">{{ error }}</p>
              <button
                type="submit"
                :disabled="saving"
                class="rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50 dark:focus:ring-offset-gray-900"
              >
                {{ saving ? "Saving..." : "Save changes" }}
              </button>
            </div>
          </form>

          <!-- Change Password -->
          <form
            class="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
            @submit.prevent="handleChangePassword"
          >
            <h2 class="mb-3 text-sm font-semibold text-gray-900 dark:text-white">Change Password</h2>

            <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <!-- Current Password -->
              <div>
                <label for="current-password" class="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
                  Current password
                </label>
                <div class="relative">
                  <input
                    id="current-password"
                    v-model="currentPassword"
                    :type="showCurrentPassword ? 'text' : 'password'"
                    required
                    class="w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 pr-9 text-sm text-gray-900 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:bg-gray-800"
                  />
                  <button
                    type="button"
                    class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    @click="showCurrentPassword = !showCurrentPassword"
                  >
                    <svg v-if="!showCurrentPassword" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12c1.292 4.338 5.31 7.5 10.066 7.5.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- New Password -->
              <div>
                <label for="new-password" class="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
                  New password
                </label>
                <div class="relative">
                  <input
                    id="new-password"
                    v-model="newPassword"
                    :type="showNewPassword ? 'text' : 'password'"
                    required
                    minlength="6"
                    class="w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 pr-9 text-sm text-gray-900 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:bg-gray-800"
                  />
                  <button
                    type="button"
                    class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    @click="showNewPassword = !showNewPassword"
                  >
                    <svg v-if="!showNewPassword" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12c1.292 4.338 5.31 7.5 10.066 7.5.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Confirm New Password -->
              <div>
                <label for="confirm-password" class="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
                  Confirm new password
                </label>
                <input
                  id="confirm-password"
                  v-model="confirmPassword"
                  type="password"
                  required
                  minlength="6"
                  class="w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:bg-gray-800"
                />
              </div>
            </div>

            <div class="mt-4 flex items-center justify-end gap-3">
              <p v-if="passwordSuccess" class="text-xs text-green-600 dark:text-green-400">{{ passwordSuccess }}</p>
              <p v-if="passwordError" class="text-xs text-red-600 dark:text-red-400">{{ passwordError }}</p>
              <button
                type="submit"
                :disabled="changingPassword"
                class="rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50 dark:focus:ring-offset-gray-900"
              >
                {{ changingPassword ? "Changing..." : "Change password" }}
              </button>
            </div>
          </form>

        </div>
      </div>
    </div>
  </AppLayout>
</template>
