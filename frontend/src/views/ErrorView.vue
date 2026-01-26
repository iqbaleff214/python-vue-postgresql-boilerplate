<script setup lang="ts">
import { computed } from "vue"
import { useRoute } from "vue-router"
import ThemeToggle from "@/components/ThemeToggle.vue"

const route = useRoute()

const statusCode = computed(() => {
  const code = route.query.code
  return code ? Number(code) : 404
})

const message = computed(() => {
  if (route.query.message) return String(route.query.message)
  switch (statusCode.value) {
    case 403:
      return "You don't have permission to access this page."
    case 404:
      return "The page you're looking for doesn't exist or has been moved."
    case 500:
      return "Something went wrong on our end. Please try again later."
    default:
      return "An unexpected error occurred."
  }
})

const title = computed(() => {
  switch (statusCode.value) {
    case 403:
      return "Forbidden"
    case 404:
      return "Page not found"
    case 500:
      return "Server error"
    default:
      return "Error"
  }
})
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-gray-100 px-4 dark:bg-gray-950">
    <div class="absolute right-4 top-4">
      <ThemeToggle />
    </div>

    <div class="text-center">
      <p class="text-7xl font-bold text-violet-600 dark:text-violet-400">
        {{ statusCode }}
      </p>
      <h1 class="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
        {{ title }}
      </h1>
      <p class="mt-2 max-w-md text-sm text-gray-500 dark:text-gray-400">
        {{ message }}
      </p>
      <div class="mt-8 flex items-center justify-center gap-3">
        <router-link
          to="/"
          class="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-gray-950"
        >
          Go to home
        </router-link>
        <button
          class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
          @click="$router.back()"
        >
          Go back
        </button>
      </div>
    </div>
  </div>
</template>
