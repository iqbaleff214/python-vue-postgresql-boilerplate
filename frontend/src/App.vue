<script setup lang="ts">
import { useThemeStore } from "@/stores/theme"

// Initialize theme on app load
useThemeStore()
</script>

<template>
  <router-view />
</template>
