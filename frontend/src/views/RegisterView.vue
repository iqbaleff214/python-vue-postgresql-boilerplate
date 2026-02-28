<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import AuthLayout from "@/components/AuthLayout.vue"

declare const google: any
declare const FB: any

const router = useRouter()
const auth = useAuthStore()

const name = ref("")
const surname = ref("")
const email = ref("")
const phoneNumber = ref("")
const password = ref("")
const showPassword = ref(false)
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

async function handleGoogleLogin() {
  error.value = ""
  google.accounts.id.initialize({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    callback: async ({ credential }: { credential: string }) => {
      loading.value = true
      try {
        await auth.signupWithGoogle(credential)
        router.push({ name: "dashboard" })
      } catch (err: any) {
        error.value = err.response?.data?.detail || "Google signup failed"
      } finally {
        loading.value = false
      }
    },
  })
  google.accounts.id.prompt()
}

async function handleFacebookLogin() {
  error.value = ""
  FB.login(async (res: any) => {
    if (res.authResponse) {
      loading.value = true
      try {
        await auth.signupWithFacebook(res.authResponse.accessToken)
        router.push({ name: "dashboard" })
      } catch (err: any) {
        error.value = err.response?.data?.detail || "Facebook signup failed"
      } finally {
        loading.value = false
      }
    }
  }, { scope: "public_profile,email" })
}

onMounted(() => {
  if (typeof FB !== "undefined") {
    FB.init({ appId: import.meta.env.VITE_FACEBOOK_APP_ID, cookie: true, xfbml: false, version: "v22.0" })
  }
})
</script>

<template>
  <AuthLayout>
    <!-- Heading -->
    <h1
      class="text-3xl font-bold tracking-tight text-gray-900 dark:text-white"
    >
      Create an account
    </h1>
    <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
      Already have an account?
      <router-link
        to="/login"
        class="font-medium text-violet-600 hover:underline dark:text-violet-400"
      >
        Log in
      </router-link>
    </p>

    <!-- Error -->
    <div
      v-if="error"
      class="mt-6 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400"
    >
      {{ error }}
    </div>

    <!-- Form -->
    <form class="mt-8 space-y-5" @submit.prevent="handleRegister">
      <!-- Name + Surname (side by side) -->
      <div class="grid grid-cols-2 gap-3">
        <input
          v-model="name"
          type="text"
          required
          placeholder="First name"
          class="w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
        />
        <input
          v-model="surname"
          type="text"
          placeholder="Last name"
          class="w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
        />
      </div>

      <!-- Email -->
      <div>
        <input
          v-model="email"
          type="email"
          required
          placeholder="Email"
          class="w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
        />
      </div>

      <!-- Phone Number -->
      <div>
        <input
          v-model="phoneNumber"
          type="tel"
          required
          placeholder="Phone number"
          class="w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 transition focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-100 dark:placeholder-gray-500 dark:focus:bg-gray-800"
        />
      </div>

      <!-- Password -->
      <div class="relative">
        <input
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          required
          minlength="6"
          placeholder="Enter your password"
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

      <!-- Submit -->
      <button
        type="submit"
        :disabled="loading"
        class="w-full rounded-xl bg-violet-600 py-3 text-sm font-semibold text-white transition hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 disabled:opacity-50 dark:focus:ring-offset-gray-950"
      >
        {{ loading ? "Creating account..." : "Create account" }}
      </button>
    </form>

    <!-- Divider -->
    <div class="relative mt-8">
      <div class="absolute inset-0 flex items-center">
        <div
          class="w-full border-t border-gray-200 dark:border-gray-800"
        />
      </div>
      <div class="relative flex justify-center text-xs">
        <span
          class="bg-gray-100 px-3 text-gray-400 dark:bg-gray-950 dark:text-gray-500"
        >
          Or register with
        </span>
      </div>
    </div>

    <!-- Social Buttons -->
    <div class="mt-6 grid grid-cols-2 gap-3">
      <button
        type="button"
        :disabled="loading"
        class="flex items-center justify-center gap-2 rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-300 dark:hover:bg-gray-800"
        @click="handleGoogleLogin"
      >
        <svg class="h-5 w-5" viewBox="0 0 24 24">
          <path
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
            fill="#4285F4"
          />
          <path
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            fill="#34A853"
          />
          <path
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            fill="#FBBC05"
          />
          <path
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            fill="#EA4335"
          />
        </svg>
        Google
      </button>
      <button
        type="button"
        :disabled="loading"
        class="flex items-center justify-center gap-2 rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-300 dark:hover:bg-gray-800"
        @click="handleFacebookLogin"
      >
        <svg class="h-5 w-5" fill="#1877F2" viewBox="0 0 24 24">
          <path d="M24 12.073C24 5.404 18.627 0 12 0S0 5.404 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.235 2.686.235v2.97h-1.513c-1.491 0-1.956.93-1.956 1.885v2.27h3.328l-.532 3.49H13.875V24C19.612 23.094 24 18.1 24 12.073z"/>
        </svg>
        Facebook
      </button>
    </div>
  </AuthLayout>
</template>
