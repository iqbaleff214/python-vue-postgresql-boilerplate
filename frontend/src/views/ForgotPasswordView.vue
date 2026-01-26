<script setup lang="ts">
import { ref } from "vue"
import { authService } from "@/services/auth"
import AuthLayout from "@/components/AuthLayout.vue"

const email = ref("")
const error = ref("")
const success = ref(false)
const loading = ref(false)

async function handleSubmit() {
  error.value = ""
  loading.value = true
  try {
    await authService.forgotPassword({ email: email.value })
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
      Forgot password?
    </h1>
    <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
      Remember your password?
      <router-link
        to="/login"
        class="font-medium text-violet-600 hover:underline dark:text-violet-400"
      >
        Back to login
      </router-link>
    </p>

    <!-- Success Message -->
    <div
      v-if="success"
      class="mt-6 rounded-lg bg-green-50 p-4 text-sm text-green-700 dark:bg-green-900/20 dark:text-green-400"
    >
      <p class="font-medium">Check your email</p>
      <p class="mt-1">
        If an account with that email exists, we've sent a password reset link.
        Please check your inbox and spam folder.
      </p>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="mt-6 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400"
    >
      {{ error }}
    </div>

    <!-- Form (hidden after success) -->
    <form v-if="!success" class="mt-8 space-y-5" @submit.prevent="handleSubmit">
      <!-- Email -->
      <div>
        <input
          v-model="email"
          type="email"
          required
          placeholder="Enter your email address"
          class="w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
        />
      </div>

      <!-- Submit -->
      <button
        type="submit"
        :disabled="loading"
        class="w-full rounded-xl bg-violet-600 py-3 text-sm font-semibold text-white transition hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50 dark:focus:ring-offset-gray-950"
      >
        {{ loading ? "Sending..." : "Send reset link" }}
      </button>
    </form>
  </AuthLayout>
</template>
