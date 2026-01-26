<script setup lang="ts">
import { ref, onMounted } from "vue"
import AppLayout from "@/components/AppLayout.vue"
import { useAuthStore } from "@/stores/auth"

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
                :src="avatarPreview || resolveAvatarUrl(auth.user?.avatar_url)!"
                alt="Avatar"
                class="h-full w-full object-cover"
              />
            </div>
            <div
              v-else
              class="flex h-20 w-20 items-center justify-center rounded-full bg-blue-600 text-2xl font-semibold text-white"
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
                class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
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
                class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
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
              class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
            />
          </div>
        </div>

        <!-- Submit -->
        <div class="mt-6 flex justify-end">
          <button
            type="submit"
            :disabled="saving"
            class="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 dark:focus:ring-offset-gray-900"
          >
            {{ saving ? "Saving..." : "Save changes" }}
          </button>
        </div>
      </form>
    </div>
  </AppLayout>
</template>
