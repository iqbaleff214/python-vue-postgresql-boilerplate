<script setup lang="ts">
import AppLayout from "@/components/AppLayout.vue"
import UserAvatar from "@/components/UserAvatar.vue"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
</script>

<template>
  <AppLayout>
    <!-- Main Content -->
    <div class="space-y-6">
      <!-- Page Header -->
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Welcome back, {{ auth.user?.name }}
        </p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <div
          class="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900"
        >
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
            Role
          </p>
          <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
            {{ auth.user?.role }}
          </p>
        </div>
        <div
          class="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900"
        >
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
            Email
          </p>
          <p
            class="mt-2 truncate text-lg font-semibold text-gray-900 dark:text-white"
          >
            {{ auth.user?.email }}
          </p>
        </div>
        <div
          class="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900"
        >
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
            Phone
          </p>
          <p class="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
            {{ auth.user?.phone_number }}
          </p>
        </div>
      </div>

      <!-- Placeholder Content -->
      <div
        class="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900"
      >
        <h2
          class="mb-4 text-lg font-semibold text-gray-900 dark:text-white"
        >
          Getting Started
        </h2>
        <p class="text-sm leading-relaxed text-gray-600 dark:text-gray-400">
          This is the main content area. Build your dashboard here by adding
          tables, charts, and action items. The layout supports an optional
          right sidebar via the <code class="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">sidebar</code> slot.
        </p>
      </div>
    </div>

    <!-- Right Sidebar -->
    <template #sidebar>
      <div class="space-y-4">
        <!-- User Card -->
        <div
          class="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
        >
          <h3
            class="mb-3 text-sm font-semibold text-gray-900 dark:text-white"
          >
            Profile
          </h3>
          <div class="flex items-center gap-3">
            <UserAvatar :name="auth.user?.name ?? ''" :avatar-url="auth.user?.avatar_url" size="md" />
            <div class="min-w-0">
              <p
                class="truncate text-sm font-medium text-gray-900 dark:text-white"
              >
                {{ auth.user?.name }}
                <span v-if="auth.user?.surname">
                  {{ auth.user?.surname }}
                </span>
              </p>
              <p
                class="truncate text-xs text-gray-500 dark:text-gray-400"
              >
                {{ auth.user?.email }}
              </p>
            </div>
          </div>
        </div>

        <!-- Alerts Placeholder -->
        <div
          class="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
        >
          <div class="mb-3 flex items-center justify-between">
            <h3
              class="text-sm font-semibold text-gray-900 dark:text-white"
            >
              Notifications
            </h3>
            <span class="text-xs text-violet-600 dark:text-violet-400">
              Mark all read
            </span>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            No new notifications.
          </p>
        </div>
      </div>
    </template>
  </AppLayout>
</template>
