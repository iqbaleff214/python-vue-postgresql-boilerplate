<script setup lang="ts">
import AppLayout from "@/components/AppLayout.vue"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
</script>

<template>
  <AppLayout>
    <div class="rounded-lg bg-white p-6 shadow">
      <h1 class="mb-2 text-2xl font-bold text-gray-900">
        Welcome, {{ auth.user?.name }}
      </h1>
      <p class="text-gray-600">
        You are logged in as
        <span class="font-medium">{{ auth.user?.email }}</span>
        with role
        <span class="rounded bg-blue-100 px-2 py-0.5 text-sm font-medium text-blue-800">
          {{ auth.user?.role }}
        </span>
      </p>
    </div>
  </AppLayout>
</template>
