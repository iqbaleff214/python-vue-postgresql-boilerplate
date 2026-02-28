
<script setup lang="ts">
import ThemeToggle from "@/components/ThemeToggle.vue"

const appName = import.meta.env.VITE_APP_NAME || "Python Vue Boilerplate";
const features = [
  {
    icon: "M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.16 2.274.283 3.423.369a.75.75 0 01.695.75v2.224a.75.75 0 001.13.65l3.418-1.93a.75.75 0 01.368-.098h1.03c1.584 0 2.707-1.627 2.707-3.227V8.063c0-1.6-1.123-2.994-2.707-3.227a48.585 48.585 0 00-7.486 0C4.622 5.069 3.5 6.463 3.5 8.063v4.876z",
    text: "Real-time notifications & alerts",
  },
  // {
  //   icon: "M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z",
  //   text: "AI-powered analysis",
  // },
  {
    icon: "M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244",
    text: "Social login with OAuth providers",
  },
  {
    icon: "M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z",
    text: "Analytics & reporting dashboard",
  },
];
</script>

<template>
  <div class="flex min-h-screen bg-gray-50 dark:bg-gray-950">
    <!-- ── Left Hero Panel ── -->
    <div class="relative hidden w-[45%] overflow-hidden lg:flex lg:flex-col">
      <!-- Base gradient -->
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950 via-indigo-900 to-purple-900" />
      <!-- <div class="absolute inset-0 bg-gradient-to-br from-rose-600 via-rose-700 to-indigo-900" /> -->

      <!-- Dot grid overlay -->
      <div
        class="absolute inset-0 opacity-[0.07]"
        style="background-image: radial-gradient(circle, white 1px, transparent 1px); background-size: 24px 24px"
      />

      <!-- Ambient glow blobs -->
      <div class="absolute -top-40 -right-40 h-[28rem] w-[28rem] rounded-full bg-rose-400/25 blur-3xl" />
      <div class="absolute -bottom-40 -left-40 h-[28rem] w-[28rem] rounded-full bg-indigo-500/25 blur-3xl" />
      <div class="absolute top-1/2 left-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-purple-400/15 blur-2xl" />

      <!-- Content -->
      <div class="relative flex h-full flex-col p-10">
        <!-- Brand -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div
              class="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 ring-1 ring-white/25 backdrop-blur-sm"
            >
              <!-- Signal / monitoring icon -->
              <span class="text-white">
                <svg xmlns="http://www.w3.org/2000/svg" 
                  width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-brand-python">
                  <path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 9h-7a2 2 0 0 0 -2 2v4a2 2 0 0 0 2 2h3" /><path d="M12 15h7a2 2 0 0 0 2 -2v-4a2 2 0 0 0 -2 -2h-3" /><path d="M8 9v-4a2 2 0 0 1 2 -2h4a2 2 0 0 1 2 2v5a2 2 0 0 1 -2 2h-4a2 2 0 0 0 -2 2v5a2 2 0 0 0 2 2h4a2 2 0 0 0 2 -2v-4" /><path d="M11 6l0 .01" /><path d="M13 18l0 .01" />
                </svg>
              </span>
            </div>
            <span class="text-lg font-semibold tracking-tight text-white">{{ appName }}</span>
          </div>
          <ThemeToggle />
        </div>

        <!-- Middle content -->
        <div class="flex flex-1 flex-col justify-center">
          <!-- Live badge -->
          <div
            class="mb-6 inline-flex w-fit items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 ring-1 ring-white/20"
          >
            <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            <span class="text-xs font-medium text-white/80">Boilerplate</span>
          </div>

          <!-- Headline -->
          <h2 class="text-4xl font-bold leading-[1.15] tracking-tight text-white">
            Build Fast,<br />
            <span class="text-rose-200">Ship Faster.</span>
          </h2>
          <p class="mt-5 max-w-sm text-[15px] leading-relaxed text-rose-100/70">
            A production-ready boilerplate for modern web applications with Python and Vue.js.
          </p>

          <!-- Feature list -->
          <ul class="mt-8 space-y-3">
            <li v-for="feature in features" :key="feature.text" class="flex items-center gap-3">
              <div
                class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-white/10 ring-1 ring-white/15"
              >
                <svg class="h-3.5 w-3.5 text-rose-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" :d="feature.icon" />
                </svg>
              </div>
              <span class="text-sm text-white/70">{{ feature.text }}</span>
            </li>
          </ul>
        </div>

        <!-- Platform badges -->
        <div>
          <p class="mb-3 text-[11px] font-semibold uppercase tracking-widest text-white/35">
            404 Not Found Indonesia © 2026
          </p>
          <div class="flex items-center gap-2.5">
            <!-- GitHub -->
            <a class="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 ring-1 ring-white/15" href="https://github.com/404NotFoundIndonesia" target="_blank" rel="noopener">
              <span class="text-indigo-300">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-brand-github"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5" /></svg>
              </span>
              <span class="text-xs font-medium text-white/70">GitHub</span>
            </a>
            <!-- Email -->
            <a class="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 ring-1 ring-white/15" href="mailto:404nf.oa@gmail.com" target="_blank" rel="noopener">
              <span class="text-indigo-300">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-mail-opened"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M14.872 14.287l6.522 6.52a2.996 2.996 0 0 1 -2.218 1.188l-.176 .005h-14a2.995 2.995 0 0 1 -2.394 -1.191l6.521 -6.522l2.318 1.545l.116 .066a1 1 0 0 0 .878 0l.116 -.066l2.317 -1.545z" /><path d="M2 9.535l5.429 3.62l-5.429 5.43z" /><path d="M22 9.535v9.05l-5.43 -5.43z" /><path d="M12.44 2.102l.115 .066l8.444 5.629l-8.999 6l-9 -6l8.445 -5.63a1 1 0 0 1 .994 -.065z" /></svg>
              </span>
              <span class="text-xs font-medium text-white/70">Email</span>
            </a>
            <!-- Lynk.id -->
            <a class="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 ring-1 ring-white/15" href="https://lynk.id/iqbaleff214" target="_blank" rel="noopener">
              <span class="text-indigo-300">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-shopping-cart"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M6 2a1 1 0 0 1 .993 .883l.007 .117v1.068l13.071 .935a1 1 0 0 1 .929 1.024l-.01 .114l-1 7a1 1 0 0 1 -.877 .853l-.113 .006h-12v2h10a3 3 0 1 1 -2.995 3.176l-.005 -.176l.005 -.176c.017 -.288 .074 -.564 .166 -.824h-5.342a3 3 0 1 1 -5.824 1.176l-.005 -.176l.005 -.176a3.002 3.002 0 0 1 1.995 -2.654v-12.17h-1a1 1 0 0 1 -.993 -.883l-.007 -.117a1 1 0 0 1 .883 -.993l.117 -.007h2zm0 16a1 1 0 1 0 0 2a1 1 0 0 0 0 -2m11 0a1 1 0 1 0 0 2a1 1 0 0 0 0 -2" /></svg>
              </span>
              <span class="text-xs font-medium text-white/70">Lynk.id</span>
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Right Form Panel ── -->
    <div class="flex flex-1 flex-col bg-gray-50 dark:bg-gray-950">
      <!-- Mobile header -->
      <div class="flex items-center justify-between border-b border-gray-200 px-5 py-4 dark:border-gray-800 lg:hidden">
        <div class="flex items-center gap-2.5">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-rose-600">
            <svg class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M9.348 14.651a3.75 3.75 0 010-5.303m5.304-.001a3.75 3.75 0 010 5.304m-7.425 2.122a6.75 6.75 0 010-9.546m9.546-.001a6.75 6.75 0 010 9.547" />
            </svg>
          </div>
          <span class="text-base font-semibold text-gray-900 dark:text-white">{{ appName }}</span>
        </div>
        <ThemeToggle />
      </div>

      <!-- Form area -->
      <div class="flex flex-1 items-center justify-center px-6 py-10 sm:px-10">
        <div class="w-full max-w-md">
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>