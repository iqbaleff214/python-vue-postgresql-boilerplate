<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const auth = useAuthStore()

const name = ref("")
const surname = ref("")
const email = ref("")
const phoneNumber = ref("")
const password = ref("")
const error = ref("")
const loading = ref(false)

async function handleRegister() {
  error.value = ""
  loading.value = true
  try {
    await auth.register({
      name: name.value,
      surname: surname.value || undefined,
      email: email.value,
      phone_number: phoneNumber.value,
      password: password.value,
    })
    router.push({ name: "dashboard" })
  } catch (err: any) {
    error.value = err.response?.data?.detail || "Registration failed"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-100">
    <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
      <h1 class="mb-6 text-center text-2xl font-bold">Create Account</h1>
      <div
        v-if="error"
        class="mb-4 rounded bg-red-100 p-3 text-red-700"
      >
        {{ error }}
      </div>
      <form class="space-y-4" @submit.prevent="handleRegister">
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">
            Name
          </label>
          <input
            v-model="name"
            type="text"
            required
            class="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">
            Surname
            <span class="text-gray-400">(optional)</span>
          </label>
          <input
            v-model="surname"
            type="text"
            class="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">
            Phone Number
          </label>
          <input
            v-model="phoneNumber"
            type="tel"
            required
            class="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="08123456789"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            v-model="password"
            type="password"
            required
            minlength="6"
            class="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-md bg-blue-600 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? "Creating account..." : "Register" }}
        </button>
      </form>
      <p class="mt-4 text-center text-sm text-gray-600">
        Already have an account?
        <router-link to="/login" class="text-blue-600 hover:underline">
          Sign In
        </router-link>
      </p>
    </div>
  </div>
</template>
