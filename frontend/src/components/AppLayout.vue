<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import ThemeToggle from "@/components/ThemeToggle.vue"
import UserAvatar from "@/components/UserAvatar.vue"

const router = useRouter()
const auth = useAuthStore()
const userMenuOpen = ref(false)
const mobileMenuOpen = ref(false)

function handleLogout() {
  auth.logout()
  router.push({ name: "login" })
}

function handleUserMenuBlur() {
  setTimeout(() => (userMenuOpen.value = false), 150)
}
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
            <slot name="nav-links" />
          </div>

          <!-- Spacer -->
          <div class="flex-1 lg:hidden" />

          <!-- Right Actions -->
          <div class="flex items-center gap-1">
            <!-- Theme Toggle -->
            <ThemeToggle />

            <!-- Notifications Bell -->
            <button
              class="relative rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-200"
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
            </button>

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
