<script setup lang="ts">
import { ref, computed, watch, nextTick } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import { useNotificationStore } from "@/stores/notifications"
import { useThemeStore } from "@/stores/theme"
import { searchService } from "@/services/search"
import type { SearchGroup, SearchItem } from "@/services/search"

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ "update:open": [value: boolean] }>()

const router = useRouter()
const auth = useAuthStore()
const themeStore = useThemeStore()
const notificationStore = useNotificationStore()

// ── State ─────────────────────────────────────────────────────────────────────
const searchQuery = ref("")
const activeIndex = ref(0)
const activeTab = ref("All")
const searchInputRef = ref<HTMLInputElement>()

const backendGroups = ref<SearchGroup[]>([])
const isSearching = ref(false)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

// ── Icon map ──────────────────────────────────────────────────────────────────
const ICONS: Record<string, string> = {
  home: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  user: "M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z",
  users: "M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z",
  document: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  sun: "M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z",
  moon: "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z",
  monitor: "M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0zM5 9h14M5 9a2 2 0 110-4h14a2 2 0 110 4M5 9v8a2 2 0 002 2h10a2 2 0 002-2V9",
  logout: "M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1",
  plus: "M12 4.5v15m7.5-7.5h-15",
}

function iconPath(name?: string): string {
  return ICONS[name ?? ""] ?? ICONS.document
}

// ── DisplayItem type ──────────────────────────────────────────────────────────
type DisplayItem = {
  id: string
  label: string
  description?: string
  icon: string
  category: string
  action: () => void
}

// ── Close ─────────────────────────────────────────────────────────────────────
function close() {
  emit("update:open", false)
  searchQuery.value = ""
  activeIndex.value = 0
  activeTab.value = "All"
  backendGroups.value = []
  isSearching.value = false
  if (debounceTimer) clearTimeout(debounceTimer)
}

// ── Built-in commands ─────────────────────────────────────────────────────────
type BuiltinCommand = {
  id: string
  label: string
  description?: string
  category: string
  icon: string
  action: () => void
  keywords?: string[]
}

const builtinCommands = computed<BuiltinCommand[]>(() => {
  const cmds: BuiltinCommand[] = [
    {
      id: "nav-dashboard",
      label: "Dashboard",
      description: "Go to the main dashboard",
      category: "Navigation",
      icon: "home",
      action: () => { router.push("/"); close() },
      keywords: ["home", "main", "overview"],
    },
    {
      id: "nav-profile",
      label: "Profile",
      description: "View and edit your profile",
      category: "Navigation",
      icon: "user",
      action: () => { router.push("/profile"); close() },
      keywords: ["account", "settings", "avatar", "password"],
    },
  ]

  if (auth.user?.role === "ADMIN") {
    cmds.push({
      id: "nav-accounts",
      label: "Accounts",
      description: "Manage user accounts",
      category: "Navigation",
      icon: "users",
      action: () => { router.push("/a/accounts"); close() },
      keywords: ["users", "admin", "manage"],
    })
  }

  cmds.push(
    {
      id: "theme-light",
      label: "Switch to Light Theme",
      description: "Use the light color scheme",
      category: "Theme",
      icon: "sun",
      action: () => { themeStore.setMode("light"); close() },
      keywords: ["appearance", "bright"],
    },
    {
      id: "theme-dark",
      label: "Switch to Dark Theme",
      description: "Use the dark color scheme",
      category: "Theme",
      icon: "moon",
      action: () => { themeStore.setMode("dark"); close() },
      keywords: ["appearance", "night"],
    },
    {
      id: "theme-system",
      label: "Use System Theme",
      description: "Follow the OS color scheme",
      category: "Theme",
      icon: "monitor",
      action: () => { themeStore.setMode("system"); close() },
      keywords: ["appearance", "auto"],
    },
    {
      id: "action-logout",
      label: "Sign Out",
      description: "Sign out of your account",
      category: "Account",
      icon: "logout",
      action: () => {
        notificationStore.reset()
        auth.logout()
        router.push({ name: "login" })
        close()
      },
      keywords: ["logout", "exit"],
    },
  )

  return cmds
})

// ── Filtering & grouping ──────────────────────────────────────────────────────
type DisplayGroup = { name: string; items: DisplayItem[] }

const allGroups = computed((): DisplayGroup[] => {
  const query = searchQuery.value.toLowerCase().trim()

  // Filter built-in commands
  const filtered = query
    ? builtinCommands.value.filter((cmd) => {
        const hay = [cmd.label, cmd.description ?? "", ...(cmd.keywords ?? [])].join(" ").toLowerCase()
        return hay.includes(query)
      })
    : builtinCommands.value

  // Group built-in commands by category
  const grouped: Record<string, DisplayItem[]> = {}
  for (const cmd of filtered) {
    if (!grouped[cmd.category]) grouped[cmd.category] = []
    grouped[cmd.category].push({
      id: cmd.id,
      label: cmd.label,
      description: cmd.description,
      icon: iconPath(cmd.icon),
      category: cmd.category,
      action: cmd.action,
    })
  }

  const groups: DisplayGroup[] = Object.entries(grouped).map(([name, items]) => ({ name, items }))

  // Append backend result groups
  for (const g of backendGroups.value) {
    groups.push({
      name: g.category,
      items: g.items.map((item: SearchItem) => ({
        id: `be-${item.id}`,
        label: item.label,
        description: item.description,
        icon: iconPath(item.icon),
        category: g.category,
        action: () => { if (item.url) router.push(item.url); close() },
      })),
    })
  }

  return groups
})

// ── Tabs ──────────────────────────────────────────────────────────────────────
// Show tabs only when there are 2+ groups.
const tabs = computed((): string[] => {
  if (allGroups.value.length < 2) return []
  return ["All", ...allGroups.value.map((g) => g.name)]
})

// Ensure activeTab is valid when groups change
watch(tabs, (newTabs) => {
  if (newTabs.length > 0 && !newTabs.includes(activeTab.value)) {
    activeTab.value = "All"
  }
})

// Groups visible under the current tab
const visibleGroups = computed((): DisplayGroup[] => {
  if (activeTab.value === "All" || tabs.value.length === 0) return allGroups.value
  return allGroups.value.filter((g) => g.name === activeTab.value)
})

// Flat list of all visible items for arrow-key navigation
const visibleItems = computed((): DisplayItem[] => {
  const out: DisplayItem[] = []
  for (const g of visibleGroups.value) {
    for (const item of g.items) out.push(item)
  }
  return out
})

const isEmpty = computed(() => !isSearching.value && visibleItems.value.length === 0)

function itemIndex(item: DisplayItem): number {
  return visibleItems.value.findIndex((i) => i.id === item.id)
}

function isActive(item: DisplayItem): boolean {
  return itemIndex(item) === activeIndex.value
}

// ── Tab switching ─────────────────────────────────────────────────────────────
function switchTab(tab: string) {
  activeTab.value = tab
  activeIndex.value = 0
}

function cycleTab(dir: 1 | -1) {
  const t = tabs.value
  if (t.length === 0) return
  const i = t.indexOf(activeTab.value)
  switchTab(t[(i + dir + t.length) % t.length])
}

// ── Keyboard ──────────────────────────────────────────────────────────────────
function scrollActive() {
  nextTick(() => {
    document.querySelector("[data-active-item='true']")?.scrollIntoView({ block: "nearest" })
  })
}

function onKeydown(e: KeyboardEvent) {
  // Tab / Shift+Tab → cycle tabs
  if (e.key === "Tab" && tabs.value.length > 0) {
    e.preventDefault()
    cycleTab(e.shiftKey ? -1 : 1)
    return
  }

  const total = visibleItems.value.length
  if (!total) return

  if (e.key === "ArrowDown") {
    e.preventDefault()
    activeIndex.value = (activeIndex.value + 1) % total
    scrollActive()
  } else if (e.key === "ArrowUp") {
    e.preventDefault()
    activeIndex.value = (activeIndex.value - 1 + total) % total
    scrollActive()
  } else if (e.key === "Enter") {
    e.preventDefault()
    visibleItems.value[activeIndex.value]?.action()
  }
}

// ── Debounced backend search ──────────────────────────────────────────────────
watch(searchQuery, (q) => {
  activeIndex.value = 0
  if (debounceTimer) clearTimeout(debounceTimer)
  if (!q.trim()) {
    backendGroups.value = []
    isSearching.value = false
    return
  }
  isSearching.value = true
  debounceTimer = setTimeout(async () => {
    try {
      const res = await searchService.search(q)
      backendGroups.value = res.groups
    } catch {
      backendGroups.value = []
    } finally {
      isSearching.value = false
    }
  }, 300)
})

watch(activeTab, () => { activeIndex.value = 0 })

watch(
  () => props.open,
  (val) => {
    if (val) {
      searchQuery.value = ""
      activeIndex.value = 0
      activeTab.value = "All"
      backendGroups.value = []
      nextTick(() => searchInputRef.value?.focus())
    }
  },
)

// ── Text highlight ────────────────────────────────────────────────────────────
function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
}

function highlight(text: string): string {
  const q = searchQuery.value.trim()
  if (!q) return escapeHtml(text)
  const safe = q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  return escapeHtml(text).replace(
    new RegExp(`(${safe})`, "gi"),
    '<mark class="bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300 rounded-sm not-italic">$1</mark>',
  )
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-start justify-center px-4 pt-[15vh]"
        @keydown="onKeydown"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="close" />

        <!-- Dialog -->
        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="opacity-0 scale-95 translate-y-1"
          enter-to-class="opacity-100 scale-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="opacity-100 scale-100 translate-y-0"
          leave-to-class="opacity-0 scale-95 translate-y-1"
          appear
        >
          <div
            class="relative w-full max-w-xl overflow-hidden rounded-xl border border-gray-200 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-900"
          >
            <!-- Search row -->
            <div class="flex items-center gap-3 border-b border-gray-200 px-4 py-3 dark:border-gray-700">
              <svg
                v-if="!isSearching"
                class="h-5 w-5 shrink-0 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <svg
                v-else
                class="h-5 w-5 shrink-0 animate-spin text-violet-500"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>

              <input
                ref="searchInputRef"
                v-model="searchQuery"
                type="text"
                placeholder="Search commands and data..."
                class="min-w-0 flex-1 bg-transparent text-sm text-gray-900 placeholder-gray-400 focus:outline-none dark:text-gray-100 dark:placeholder-gray-500"
                @keydown.esc="close"
              />
              <kbd class="hidden shrink-0 rounded border border-gray-200 bg-gray-100 px-1.5 py-0.5 font-mono text-[10px] text-gray-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400 sm:block">
                Esc
              </kbd>
            </div>

            <!-- Tab bar (shown when 2+ groups) -->
            <div
              v-if="tabs.length > 0"
              class="flex items-center gap-0.5 overflow-x-auto border-b border-gray-200 px-3 dark:border-gray-700"
            >
              <button
                v-for="tab in tabs"
                :key="tab"
                class="shrink-0 rounded-t px-3 py-2 text-xs font-medium transition-colors focus:outline-none"
                :class="
                  activeTab === tab
                    ? 'border-b-2 border-violet-600 text-violet-600 dark:border-violet-400 dark:text-violet-400'
                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                "
                @click="switchTab(tab)"
              >
                {{ tab }}
              </button>
            </div>

            <!-- Results -->
            <div class="max-h-72 overflow-y-auto py-2">
              <!-- Loading skeleton -->
              <div v-if="isSearching && backendGroups.length === 0" class="space-y-1 px-3 py-2">
                <div v-for="n in 3" :key="n" class="flex items-center gap-3 rounded-lg px-2 py-2">
                  <div class="h-8 w-8 animate-pulse rounded-md bg-gray-100 dark:bg-gray-800" />
                  <div class="flex-1 space-y-1.5">
                    <div class="h-3 w-2/5 animate-pulse rounded bg-gray-100 dark:bg-gray-800" />
                    <div class="h-2.5 w-3/5 animate-pulse rounded bg-gray-100 dark:bg-gray-800" />
                  </div>
                </div>
              </div>

              <!-- Empty state -->
              <div
                v-else-if="isEmpty"
                class="py-10 text-center text-sm text-gray-500 dark:text-gray-400"
              >
                No results for
                <span class="font-medium text-gray-700 dark:text-gray-300">"{{ searchQuery }}"</span>
              </div>

              <!-- Groups -->
              <template v-else>
                <div v-for="group in visibleGroups" :key="group.name">
                  <div
                    class="mb-1 px-4 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500"
                  >
                    {{ group.name }}
                  </div>

                  <button
                    v-for="item in group.items"
                    :key="item.id"
                    :data-active-item="isActive(item)"
                    class="mx-1 flex items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors"
                    :class="
                      isActive(item)
                        ? 'bg-violet-600 text-white'
                        : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                    "
                    style="width: calc(100% - 8px)"
                    @click="item.action()"
                    @mouseenter="activeIndex = itemIndex(item)"
                  >
                    <span
                      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md"
                      :class="
                        isActive(item)
                          ? 'bg-violet-500/40 text-white'
                          : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                      "
                    >
                      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" />
                      </svg>
                    </span>

                    <div class="min-w-0 flex-1">
                      <p class="truncate text-sm font-medium" v-html="highlight(item.label)" />
                      <p
                        v-if="item.description"
                        class="truncate text-xs opacity-70"
                        v-html="highlight(item.description)"
                      />
                    </div>
                  </button>
                </div>
              </template>
            </div>

            <!-- Footer -->
            <div class="flex items-center gap-4 border-t border-gray-200 px-4 py-2 dark:border-gray-700">
              <span class="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                <kbd class="rounded border border-gray-200 bg-gray-100 px-1 py-0.5 font-mono text-[10px] dark:border-gray-600 dark:bg-gray-800">↑</kbd>
                <kbd class="rounded border border-gray-200 bg-gray-100 px-1 py-0.5 font-mono text-[10px] dark:border-gray-600 dark:bg-gray-800">↓</kbd>
                navigate
              </span>
              <span class="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                <kbd class="rounded border border-gray-200 bg-gray-100 px-1.5 py-0.5 font-mono text-[10px] dark:border-gray-600 dark:bg-gray-800">↵</kbd>
                select
              </span>
              <span v-if="tabs.length > 0" class="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                <kbd class="rounded border border-gray-200 bg-gray-100 px-1.5 py-0.5 font-mono text-[10px] dark:border-gray-600 dark:bg-gray-800">Tab</kbd>
                switch tab
              </span>
              <span class="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                <kbd class="rounded border border-gray-200 bg-gray-100 px-1.5 py-0.5 font-mono text-[10px] dark:border-gray-600 dark:bg-gray-800">Esc</kbd>
                close
              </span>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
