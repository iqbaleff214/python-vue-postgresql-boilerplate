<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { authService } from "@/services/auth"
import AuthLayout from "@/components/AuthLayout.vue"

const route = useRoute()

const token = ref("")
const newPassword = ref("")
const confirmPassword = ref("")
const showPassword = ref(false)
const error = ref("")
const success = ref(false)
const loading = ref(false)
const tokenMissing = ref(false)

onMounted(() => {
  const t = route.query.token
  if (typeof t === "string" && t.length > 0) {
    token.value = t
  } else {
    tokenMissing.value = true
  }
})

async function handleSubmit() {
  error.value = ""

  if (newPassword.value !== confirmPassword.value) {
    error.value = "Passwords do not match."
    return
  }

  loading.value = true
  try {
    await authService.resetPassword({
      token: token.value,
      new_password: newPassword.value,
    })
    success.value = true
  } catch (err: any) {
    error.value = err.response?.data?.detail || "Something went wrong. Please try again."
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout>
    <!-- Heading -->
    <h1
      class="text-3xl font-bold tracking-tight text-gray-900 dark:text-white"
    >
      Reset password
    </h1>
    <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
      Enter your new password below.
    </p>

    <!-- Token Missing -->
    <div
      v-if="tokenMissing"
      class="mt-6 rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400"
    >
      <p class="font-medium">Invalid reset link</p>
      <p class="mt-1">
        This link is missing a reset token. Please request a new password reset.
      </p>
      <router-link
        to="/forgot-password"
        class="mt-3 inline-block font-medium text-violet-600 hover:underline dark:text-violet-400"
      >
        Request new reset link
      </router-link>
    </div>

    <!-- Success Message -->
    <div
      v-if="success"
      class="mt-6 rounded-lg bg-green-50 p-4 text-sm text-green-700 dark:bg-green-900/20 dark:text-green-400"
    >
      <p class="font-medium">Password reset successful</p>
      <p class="mt-1">
        Your password has been updated. You can now log in with your new password.
      </p>
      <router-link
        to="/login"
        class="mt-3 inline-block font-medium text-violet-600 hover:underline dark:text-violet-400"
      >
        Go to login
      </router-link>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="mt-6 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400"
    >
      {{ error }}
    </div>

    <!-- Form (hidden after success or if token missing) -->
    <form
      v-if="!success && !tokenMissing"
      class="mt-8 space-y-5"
      @submit.prevent="handleSubmit"
    >
      <!-- New Password -->
      <div class="relative">
        <input
          v-model="newPassword"
          :type="showPassword ? 'text' : 'password'"
          required
          minlength="6"
          placeholder="New password"
          class="w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 pr-11 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
        />
        <button
          type="button"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          @click="showPassword = !showPassword"
        >
          <!-- Eye open -->
          <svg
            v-if="!showPassword"
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
          <!-- Eye closed -->
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

      <!-- Confirm Password -->
      <div>
        <input
          v-model="confirmPassword"
          :type="showPassword ? 'text' : 'password'"
          required
          minlength="6"
          placeholder="Confirm new password"
          class="w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
        />
      </div>

      <!-- Submit -->
      <button
        type="submit"
        :disabled="loading"
        class="w-full rounded-xl bg-violet-600 py-3 text-sm font-semibold text-white transition hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50 dark:focus:ring-offset-gray-950"
      >
        {{ loading ? "Resetting..." : "Reset password" }}
      </button>
    </form>
  </AuthLayout>
</template>
