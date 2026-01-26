import { ref, watch } from "vue"
import { defineStore } from "pinia"

type ThemeMode = "light" | "dark" | "system"

function getSystemPreference(): boolean {
  return window.matchMedia("(prefers-color-scheme: dark)").matches
}

function applyTheme(mode: ThemeMode) {
  const isDark = mode === "dark" || (mode === "system" && getSystemPreference())
  document.documentElement.classList.toggle("dark", isDark)
}

export const useThemeStore = defineStore("theme", () => {
  const mode = ref<ThemeMode>(
    (localStorage.getItem("theme") as ThemeMode) || "system",
  )

  function setMode(newMode: ThemeMode) {
    mode.value = newMode
    localStorage.setItem("theme", newMode)
    applyTheme(newMode)
  }

  // React to store changes
  watch(mode, (m) => applyTheme(m), { immediate: true })

  // React to OS preference changes when in system mode
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      if (mode.value === "system") {
        applyTheme("system")
      }
    })

  return { mode, setMode }
})
