<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import { useNotificationStore } from "@/stores/notifications"
import ThemeToggle from "@/components/ThemeToggle.vue"
import UserAvatar from "@/components/UserAvatar.vue"

const router = useRouter()
const auth = useAuthStore()
const notificationStore = useNotificationStore()

const userMenuOpen = ref(false)
const mobileMenuOpen = ref(false)
const notificationsOpen = ref(false)

function handleLogout() {
  notificationStore.reset()
  auth.logout()
  router.push({ name: "login" })
}

function handleUserMenuBlur() {
  setTimeout(() => (userMenuOpen.value = false), 150)
}

function handleNotificationsBlur() {
  setTimeout(() => (notificationsOpen.value = false), 150)
}

function handleNotificationClick(notification: (typeof notificationStore.notifications)[0]) {
  if (!notification.is_read) {
    notificationStore.markAsRead([notification.id])
  }
  if (notification.link) {
    router.push(notification.link)
    notificationsOpen.value = false
  }
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (seconds < 60) return "Just now"
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`
  return date.toLocaleDateString()
}

function getNotificationIcon(type: string): string {
  switch (type) {
    case "success":
      return "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
    case "warning":
      return "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
    case "error":
      return "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
    default:
      return "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
  }
}

function getNotificationColor(type: string): string {
  switch (type) {
    case "success":
      return "text-green-500"
    case "warning":
      return "text-yellow-500"
    case "error":
      return "text-red-500"
    default:
      return "text-blue-500"
  }
}

// Connect/disconnect WebSocket based on auth state
watch(
  () => auth.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      notificationStore.connectWebSocket()
      notificationStore.fetchNotifications({ limit: 10 })
    } else {
      notificationStore.reset()
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  notificationStore.disconnectWebSocket()
})
</script>

<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-950">
    <!-- Top Navigation -->
    <nav
      class="sticky top-0 z-40 border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900"
    >
      <div class="mx-auto max-w-full px-4 sm:px-6 lg:px-8">
        <div class="flex h-14 items-center gap-4">
          <!-- Brand -->
          <div class="flex shrink-0 items-center gap-2">
            <div
              class="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-600 text-sm font-bold text-white"
            >
              PV
            </div>
            <span
              class="hidden text-base font-semibold text-gray-900 dark:text-white sm:block"
            >
              Python Vue
            </span>
          </div>

          <!-- Search Bar -->
          <div class="hidden flex-1 md:block md:max-w-sm lg:max-w-md">
            <div class="relative">
              <svg
                class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <input
                type="text"
                placeholder="Search..."
                class="w-full rounded-lg border border-gray-200 bg-gray-50 py-1.5 pl-9 pr-3 text-sm text-gray-900 placeholder-gray-400 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500"
              />
            </div>
          </div>

          <!-- Center Nav Links -->
          <div class="hidden flex-1 items-center justify-center gap-1 lg:flex">
            <router-link
              to="/"
              class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
              active-class="!bg-gray-100 !text-gray-900 dark:!bg-gray-800 dark:!text-white"
            >
              Dashboard
            </router-link>
            <router-link
              v-if="auth.user?.role === 'ADMIN'"
              to="/a/accounts"
              class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
              active-class="!bg-gray-100 !text-gray-900 dark:!bg-gray-800 dark:!text-white"
            >
              Accounts
            </router-link>
            <slot name="nav-links" />
          </div>

          <!-- Spacer -->
          <div class="flex-1 lg:hidden" />

          <!-- Right Actions -->
          <div class="flex items-center gap-1">
            <!-- Theme Toggle -->
            <ThemeToggle />

            <!-- Notifications Bell -->
            <div class="relative">
              <button
                class="relative rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-200"
                @click="notificationsOpen = !notificationsOpen"
                @blur="handleNotificationsBlur"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
                <!-- Unread badge -->
                <span
                  v-if="notificationStore.hasUnread"
                  class="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-medium text-white"
                >
                  {{ notificationStore.displayCount }}
                </span>
                <!-- Connected indicator -->
                <span
                  v-if="notificationStore.isConnected"
                  class="absolute bottom-1 right-1 h-2 w-2 rounded-full bg-green-400"
                />
              </button>

              <!-- Notifications Dropdown -->
              <Transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="notificationsOpen"
                  class="absolute right-0 z-50 mt-2 w-80 origin-top-right rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
                >
                  <!-- Header -->
                  <div
                    class="flex items-center justify-between border-b border-gray-100 px-4 py-3 dark:border-gray-700"
                  >
                    <h3 class="text-sm font-semibold text-gray-900 dark:text-white">Notifications</h3>
                    <button
                      v-if="notificationStore.hasUnread"
                      class="text-xs text-violet-600 hover:text-violet-700 dark:text-violet-400"
                      @click="notificationStore.markAllAsRead()"
                    >
                      Mark all as read
                    </button>
                  </div>

                  <!-- Notification List -->
                  <div class="max-h-96 overflow-y-auto">
                    <div
                      v-if="notificationStore.isLoading"
                      class="flex items-center justify-center py-8"
                    >
                      <svg
                        class="h-6 w-6 animate-spin text-gray-400"
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
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                    </div>

                    <div
                      v-else-if="notificationStore.notifications.length === 0"
                      class="py-8 text-center text-sm text-gray-500 dark:text-gray-400"
                    >
                      No notifications yet
                    </div>

                    <button
                      v-else
                      v-for="notification in notificationStore.notifications"
                      :key="notification.id"
                      class="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50"
                      :class="{ 'bg-violet-50/50 dark:bg-violet-900/10': !notification.is_read }"
                      @click="handleNotificationClick(notification)"
                    >
                      <!-- Icon -->
                      <svg
                        class="mt-0.5 h-5 w-5 flex-shrink-0"
                        :class="getNotificationColor(notification.type)"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        stroke-width="2"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          :d="getNotificationIcon(notification.type)"
                        />
                      </svg>

                      <!-- Content -->
                      <div class="min-w-0 flex-1">
                        <p
                          class="text-sm font-medium text-gray-900 dark:text-white"
                          :class="{ 'font-semibold': !notification.is_read }"
                        >
                          {{ notification.title }}
                        </p>
                        <p
                          v-if="notification.message"
                          class="mt-0.5 line-clamp-2 text-xs text-gray-500 dark:text-gray-400"
                        >
                          {{ notification.message }}
                        </p>
                        <p class="mt-1 text-xs text-gray-400 dark:text-gray-500">
                          {{ formatTimeAgo(notification.created_at) }}
                        </p>
                      </div>

                      <!-- Unread dot -->
                      <span
                        v-if="!notification.is_read"
                        class="mt-2 h-2 w-2 flex-shrink-0 rounded-full bg-violet-500"
                      />
                    </button>
                  </div>

                  <!-- Footer -->
                  <div
                    v-if="notificationStore.total > notificationStore.notifications.length"
                    class="border-t border-gray-100 px-4 py-2 dark:border-gray-700"
                  >
                    <button
                      class="block w-full text-center text-xs text-violet-600 hover:text-violet-700 dark:text-violet-400"
                      @click="notificationStore.fetchNotifications({ limit: 50 })"
                    >
                      Load more notifications
                    </button>
                  </div>
                </div>
              </Transition>
            </div>

            <!-- User Menu -->
            <div v-if="auth.user" class="relative">
              <button
                class="flex items-center gap-2 rounded-lg p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700"
                @click="userMenuOpen = !userMenuOpen"
                @blur="handleUserMenuBlur"
              >
                <UserAvatar :name="auth.user.name" :avatar-url="auth.user.avatar_url" size="sm" />
              </button>

              <Transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="userMenuOpen"
                  class="absolute right-0 z-50 mt-2 w-56 origin-top-right rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800"
                >
                  <div
                    class="border-b border-gray-100 px-4 py-3 dark:border-gray-700"
                  >
                    <p
                      class="text-sm font-medium text-gray-900 dark:text-white"
                    >
                      {{ auth.user.name }}
                      <span v-if="auth.user.surname">
                        {{ auth.user.surname }}
                      </span>
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                      {{ auth.user.email }}
                    </p>
                  </div>
                  <router-link
                    to="/profile"
                    class="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                    @click="userMenuOpen = false"
                  >
                    <svg
                      class="h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
                      />
                    </svg>
                    Profile
                  </router-link>
                  <button
                    class="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                    @click="handleLogout"
                  >
                    <svg
                      class="h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                      />
                    </svg>
                    Sign out
                  </button>
                </div>
              </Transition>
            </div>

            <!-- Mobile menu toggle -->
            <button
              class="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-200 lg:hidden"
              @click="mobileMenuOpen = !mobileMenuOpen"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  v-if="!mobileMenuOpen"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M4 6h16M4 12h16M4 18h16"
                />
                <path
                  v-else
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Mobile Nav -->
        <div v-if="mobileMenuOpen" class="border-t border-gray-200 py-2 lg:hidden dark:border-gray-700">
          <router-link
            to="/"
            class="block rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
            @click="mobileMenuOpen = false"
          >
            Dashboard
          </router-link>
          <router-link
            v-if="auth.user?.role === 'ADMIN'"
            to="/a/accounts"
            class="block rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
            @click="mobileMenuOpen = false"
          >
            Accounts
          </router-link>
          <slot name="mobile-nav-links" />
        </div>
      </div>
    </nav>

    <!-- Page Content -->
    <div class="mx-auto max-w-full px-4 py-6 sm:px-6 lg:px-8">
      <div class="flex flex-col gap-6 lg:flex-row">
        <!-- Main Content -->
        <main class="min-w-0 flex-1">
          <slot />
        </main>

        <!-- Right Sidebar (optional) -->
        <aside
          v-if="$slots.sidebar"
          class="w-full shrink-0 lg:w-80"
        >
          <slot name="sidebar" />
        </aside>
      </div>
    </div>
  </div>
</template>
