<script setup lang="ts">
import { ref, onMounted } from "vue"
import AppLayout from "@/components/AppLayout.vue"
import { useAuthStore } from "@/stores/auth"
import { authService } from "@/services/auth"

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

onMounted(() => {
  if (auth.user) {
    name.value = auth.user.name
    surname.value = auth.user.surname || ""
    phoneNumber.value = auth.user.phone_number
  }
})

function resolveAvatarUrl(url: string | null | undefined): string | null {
  if (!url) return null
  if (url.startsWith("http")) return url
  const base = import.meta.env.VITE_APP_API_URL?.replace(/\/api\/?$/, "") || ""
  return `${base}${url}`
}

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
</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page Header -->
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          Profile
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Manage your personal information and avatar.
        </p>
      </div>

      <!-- Feedback Messages -->
      <div
        v-if="success"
        class="rounded-lg bg-green-50 p-3 text-sm text-green-700 dark:bg-green-900/20 dark:text-green-400"
      >
        {{ success }}
      </div>
      <div
        v-if="error"
        class="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400"
      >
        {{ error }}
      </div>

      <!-- Avatar Section -->
      <div
        class="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900"
      >
        <h2
          class="mb-4 text-lg font-semibold text-gray-900 dark:text-white"
        >
          Avatar
        </h2>
        <div class="flex items-center gap-5">
          <div class="relative">
            <div
              v-if="avatarPreview || resolveAvatarUrl(auth.user?.avatar_url)"
              class="h-20 w-20 overflow-hidden rounded-full"
            >
              <img
                :src="(avatarPreview || resolveAvatarUrl(auth.user?.avatar_url)) as string"
                alt="Avatar"
                class="h-full w-full object-cover"
              />
            </div>
            <div
              v-else
              class="flex h-20 w-20 items-center justify-center rounded-full bg-violet-600 text-2xl font-semibold text-white"
            >
              {{ auth.user?.name.charAt(0).toUpperCase() }}
            </div>
            <div
              v-if="avatarUploading"
              class="absolute inset-0 flex items-center justify-center rounded-full bg-black/40"
            >
              <svg
                class="h-6 w-6 animate-spin text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
            </div>
          </div>
          <div>
            <button
              type="button"
              :disabled="avatarUploading"
              class="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
              @click="triggerFileInput"
            >
              {{ avatarUploading ? "Uploading..." : "Change avatar" }}
            </button>
            <p class="mt-1.5 text-xs text-gray-500 dark:text-gray-400">
              JPEG, PNG, WebP or GIF. Max 5 MB.
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

      <!-- Profile Form -->
      <form
        class="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900"
        @submit.prevent="handleSave"
      >
        <h2
          class="mb-5 text-lg font-semibold text-gray-900 dark:text-white"
        >
          Personal Information
        </h2>
        <div class="space-y-4">
          <!-- Name + Surname -->
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label
                for="profile-name"
                class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                First name
              </label>
              <input
                id="profile-name"
                v-model="name"
                type="text"
                required
                class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
              />
            </div>
            <div>
              <label
                for="profile-surname"
                class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Last name
              </label>
              <input
                id="profile-surname"
                v-model="surname"
                type="text"
                class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
              />
            </div>
          </div>

          <!-- Email (read-only) -->
          <div>
            <label
              for="profile-email"
              class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Email
            </label>
            <input
              id="profile-email"
              :value="auth.user?.email"
              type="email"
              disabled
              class="w-full rounded-lg border border-gray-200 bg-gray-100 px-4 py-2.5 text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-400"
            />
            <p class="mt-1 text-xs text-gray-400 dark:text-gray-500">
              Email cannot be changed.
            </p>
          </div>

          <!-- Phone Number -->
          <div>
            <label
              for="profile-phone"
              class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Phone number
            </label>
            <input
              id="profile-phone"
              v-model="phoneNumber"
              type="tel"
              required
              class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
            />
          </div>
        </div>

        <!-- Submit -->
        <div class="mt-6 flex justify-end">
          <button
            type="submit"
            :disabled="saving"
            class="rounded-lg bg-violet-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50 dark:focus:ring-offset-gray-900"
          >
            {{ saving ? "Saving..." : "Save changes" }}
          </button>
        </div>
      </form>

      <!-- Change Password -->
      <form
        class="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900"
        @submit.prevent="handleChangePassword"
      >
        <h2
          class="mb-5 text-lg font-semibold text-gray-900 dark:text-white"
        >
          Change Password
        </h2>

        <!-- Password Feedback -->
        <div
          v-if="passwordSuccess"
          class="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700 dark:bg-green-900/20 dark:text-green-400"
        >
          {{ passwordSuccess }}
        </div>
        <div
          v-if="passwordError"
          class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400"
        >
          {{ passwordError }}
        </div>

        <div class="space-y-4">
          <!-- Current Password -->
          <div>
            <label
              for="current-password"
              class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Current password
            </label>
            <div class="relative">
              <input
                id="current-password"
                v-model="currentPassword"
                :type="showCurrentPassword ? 'text' : 'password'"
                required
                class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 pr-11 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                @click="showCurrentPassword = !showCurrentPassword"
              >
                <svg
                  v-if="!showCurrentPassword"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <svg
                  v-else
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M3.98 8.223A10.477 10.477 0 001.934 12c1.292 4.338 5.31 7.5 10.066 7.5.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
                  />
                </svg>
              </button>
            </div>
          </div>

          <!-- New Password -->
          <div>
            <label
              for="new-password"
              class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              New password
            </label>
            <div class="relative">
              <input
                id="new-password"
                v-model="newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                required
                minlength="6"
                class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 pr-11 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                @click="showNewPassword = !showNewPassword"
              >
                <svg
                  v-if="!showNewPassword"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <svg
                  v-else
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M3.98 8.223A10.477 10.477 0 001.934 12c1.292 4.338 5.31 7.5 10.066 7.5.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
                  />
                </svg>
              </button>
            </div>
          </div>

          <!-- Confirm New Password -->
          <div>
            <label
              for="confirm-password"
              class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Confirm new password
            </label>
            <input
              id="confirm-password"
              v-model="confirmPassword"
              type="password"
              required
              minlength="6"
              class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
            />
          </div>
        </div>

        <!-- Submit -->
        <div class="mt-6 flex justify-end">
          <button
            type="submit"
            :disabled="changingPassword"
            class="rounded-lg bg-violet-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50 dark:focus:ring-offset-gray-900"
          >
            {{ changingPassword ? "Changing..." : "Change password" }}
          </button>
        </div>
      </form>
    </div>
  </AppLayout>
</template>
