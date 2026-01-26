<script setup lang="ts">
import { computed } from "vue"

const props = withDefaults(
  defineProps<{
    name: string
    avatarUrl?: string | null
    size?: "sm" | "md" | "lg"
  }>(),
  {
    avatarUrl: null,
    size: "sm",
  },
)

const resolvedUrl = computed(() => {
  if (!props.avatarUrl) return null
  if (props.avatarUrl.startsWith("/")) {
    const base =
      import.meta.env.VITE_APP_API_URL?.replace(/\/api\/?$/, "") || ""
    return `${base}${props.avatarUrl}`
  }
  return props.avatarUrl
})

const initial = computed(() =>
  props.name ? props.name.charAt(0).toUpperCase() : "?",
)

const sizeClasses = computed(() => {
  switch (props.size) {
    case "sm":
      return "h-8 w-8 text-xs"
    case "md":
      return "h-10 w-10 text-sm"
    case "lg":
      return "h-20 w-20 text-2xl"
  }
})
</script>

<template>
  <div class="shrink-0 overflow-hidden rounded-full" :class="sizeClasses">
    <img
      v-if="resolvedUrl"
      :src="resolvedUrl"
      :alt="name"
      class="h-full w-full object-cover"
    />
    <div
      v-else
      class="flex h-full w-full items-center justify-center bg-violet-600 font-medium text-white"
    >
      {{ initial }}
    </div>
  </div>
</template>
