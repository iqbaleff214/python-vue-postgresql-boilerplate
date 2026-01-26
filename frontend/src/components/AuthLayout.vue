<script setup lang="ts">
import ThemeToggle from "@/components/ThemeToggle.vue"
</script>

<template>
  <div class="flex min-h-screen bg-gray-100 dark:bg-gray-950">
    <!-- Left Hero Panel -->
    <div
      class="relative hidden w-[45%] overflow-hidden lg:block"
    >
      <div
        class="absolute inset-0 bg-gradient-to-br from-violet-950 via-indigo-900 to-purple-900"
      />
      <!-- Decorative shapes -->
      <div
        class="absolute -bottom-20 -left-20 h-80 w-80 rounded-full bg-purple-500/10 blur-3xl"
      />
      <div
        class="absolute -top-20 right-0 h-64 w-64 rounded-full bg-indigo-500/10 blur-3xl"
      />
      <div
        class="absolute bottom-1/3 left-1/4 h-48 w-48 rounded-full bg-violet-400/10 blur-2xl"
      />

      <!-- Content overlay -->
      <div class="relative flex h-full flex-col justify-between p-10">
        <!-- Brand -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div
              class="flex h-9 w-9 items-center justify-center rounded-lg bg-white/10 text-sm font-bold text-white backdrop-blur-sm"
            >
              PV
            </div>
            <span class="text-base font-semibold text-white">
              Python Vue
            </span>
          </div>
          <ThemeToggle />
        </div>

        <!-- Tagline -->
        <div class="pb-10">
          <h2 class="text-3xl font-bold leading-tight text-white">
            Build Fast,<br />Ship Faster
          </h2>
          <p class="mt-3 max-w-xs text-sm leading-relaxed text-indigo-200">
            A production-ready boilerplate for modern web applications with
            Python and Vue.js.
          </p>
        </div>
      </div>
    </div>

    <!-- Right Form Panel -->
    <div class="flex flex-1 flex-col">
      <!-- Mobile header (visible below lg) -->
      <div class="flex items-center justify-between p-4 lg:hidden">
        <div class="flex items-center gap-2">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-600 text-sm font-bold text-white"
          >
            PV
          </div>
          <span
            class="text-base font-semibold text-gray-900 dark:text-white"
          >
            Python Vue
          </span>
        </div>
        <ThemeToggle />
      </div>

      <!-- Form area (vertically centered) -->
      <div
        class="flex flex-1 items-center justify-center px-6 py-8 sm:px-12 lg:px-16"
      >
        <div class="w-full max-w-md">
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>
