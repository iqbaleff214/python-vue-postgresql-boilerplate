import { ref, computed } from "vue"
import { defineStore } from "pinia"
import {
  notificationService,
  type Notification,
  type WebSocketMessage,
} from "@/services/notifications"
import notificationSoundFile from "@/assets/sound/new-notification-09-352705.mp3"

export const useNotificationStore = defineStore("notifications", () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const total = ref(0)
  const isLoading = ref(false)
  const isConnected = ref(false)
  const error = ref<string | null>(null)
  const soundEnabled = ref(true)

  let websocket: WebSocket | null = null
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null
  let pingInterval: ReturnType<typeof setInterval> | null = null
  let notificationSound: HTMLAudioElement | null = null
  let audioUnlocked = false

  function getNotificationSound(): HTMLAudioElement {
    if (!notificationSound) {
      notificationSound = new Audio(notificationSoundFile)
      notificationSound.volume = 0.5
    }
    return notificationSound
  }

  function unlockAudio() {
    if (audioUnlocked) return
    const sound = getNotificationSound()
    // Play silently to unlock audio context
    sound.volume = 0
    sound.play().then(() => {
      sound.pause()
      sound.currentTime = 0
      sound.volume = 0.5
      audioUnlocked = true
      // Remove listeners after successful unlock
      document.removeEventListener("click", unlockAudio)
      document.removeEventListener("touchstart", unlockAudio)
      document.removeEventListener("keydown", unlockAudio)
    }).catch(() => {
      // Still blocked, will try again on next interaction
    })
  }

  function initAudioUnlock() {
    if (typeof document === "undefined") return
    document.addEventListener("click", unlockAudio, { once: false })
    document.addEventListener("touchstart", unlockAudio, { once: false })
    document.addEventListener("keydown", unlockAudio, { once: false })
  }

  // Initialize audio unlock listeners
  initAudioUnlock()

  function playNotificationSound() {
    if (!soundEnabled.value) return
    if (!audioUnlocked) {
      console.debug("Audio not yet unlocked, waiting for user interaction")
      return
    }
    try {
      const sound = getNotificationSound()
      sound.currentTime = 0
      sound.play().catch((e) => {
        console.debug("Could not play notification sound:", e)
      })
    } catch (e) {
      console.debug("Failed to play notification sound:", e)
    }
  }

  function toggleSound(enabled?: boolean) {
    soundEnabled.value = enabled ?? !soundEnabled.value
  }

  const hasUnread = computed(() => unreadCount.value > 0)
  const displayCount = computed(() =>
    unreadCount.value > 99 ? "99+" : String(unreadCount.value)
  )

  async function fetchNotifications(params?: {
    limit?: number
    offset?: number
    unread_only?: boolean
  }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await notificationService.getNotifications(params)
      notifications.value = response.notifications
      unreadCount.value = response.unread_count
      total.value = response.total
    } catch (e) {
      error.value = "Failed to load notifications"
      console.error("Failed to fetch notifications:", e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUnreadCount() {
    try {
      const response = await notificationService.getUnreadCount()
      unreadCount.value = response.unread_count
    } catch (e) {
      console.error("Failed to fetch unread count:", e)
    }
  }

  async function markAsRead(notificationIds: string[]) {
    try {
      const response = await notificationService.markAsRead(notificationIds)
      unreadCount.value = response.unread_count
      // Update local state
      notifications.value = notifications.value.map((n) =>
        notificationIds.includes(n.id)
          ? { ...n, is_read: true, read_at: new Date().toISOString() }
          : n
      )
    } catch (e) {
      console.error("Failed to mark as read:", e)
    }
  }

  async function markAllAsRead() {
    try {
      const response = await notificationService.markAllAsRead()
      unreadCount.value = response.unread_count
      notifications.value = notifications.value.map((n) => ({
        ...n,
        is_read: true,
        read_at: n.read_at || new Date().toISOString(),
      }))
    } catch (e) {
      console.error("Failed to mark all as read:", e)
    }
  }

  function connectWebSocket() {
    const token = localStorage.getItem("token")
    if (!token) {
      console.warn("No token available for WebSocket connection")
      return
    }

    // Cleanup existing connection
    disconnectWebSocket()

    const apiUrl = import.meta.env.VITE_APP_API_URL || "http://localhost:8001"
    const wsUrl = apiUrl.replace("http", "ws")
    const url = `${wsUrl}/notifications/ws?token=${token}`

    try {
      websocket = new WebSocket(url)

      websocket.onopen = () => {
        console.log("WebSocket connected")
        isConnected.value = true

        // Start ping interval to keep connection alive
        pingInterval = setInterval(() => {
          if (websocket?.readyState === WebSocket.OPEN) {
            websocket.send("ping")
          }
        }, 30000) // Ping every 30 seconds
      }

      websocket.onmessage = (event) => {
        if (event.data === "pong") return // Ignore pong responses

        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          handleWebSocketMessage(message)
        } catch (e) {
          console.error("Failed to parse WebSocket message:", e)
        }
      }

      websocket.onclose = (event) => {
        console.log("WebSocket closed:", event.code, event.reason)
        isConnected.value = false
        cleanup()

        // Reconnect after 5 seconds if not intentionally closed
        if (event.code !== 4001 && event.code !== 1000) {
          scheduleReconnect()
        }
      }

      websocket.onerror = (error) => {
        console.error("WebSocket error:", error)
        isConnected.value = false
      }
    } catch (e) {
      console.error("Failed to create WebSocket:", e)
    }
  }

  function handleWebSocketMessage(message: WebSocketMessage) {
    console.log("WebSocket message received:", message.event, message.data)

    switch (message.event) {
      case "connected":
        unreadCount.value = (message.data.unread_count as number) || 0
        console.log("WebSocket connected, unread count:", unreadCount.value)
        break

      case "new_notification": {
        // Add new notification to the top of the list
        const newNotification = message.data as unknown as Notification
        notifications.value = [newNotification, ...notifications.value]
        unreadCount.value++
        total.value++
        console.log("New notification received:", newNotification.title)
        // Play notification sound
        playNotificationSound()
        break
      }

      case "notification_count":
        unreadCount.value = (message.data.unread_count as number) || 0
        break

      case "notification_read": {
        // Update read status from another tab/device
        const readIds = (message.data.notification_ids as string[]) || []
        notifications.value = notifications.value.map((n) =>
          readIds.includes(n.id) ? { ...n, is_read: true } : n
        )
        break
      }
    }
  }

  function scheduleReconnect() {
    if (reconnectTimeout) return
    reconnectTimeout = setTimeout(() => {
      reconnectTimeout = null
      const token = localStorage.getItem("token")
      if (token) {
        console.log("Attempting to reconnect WebSocket...")
        connectWebSocket()
      }
    }, 5000)
  }

  function cleanup() {
    if (pingInterval) {
      clearInterval(pingInterval)
      pingInterval = null
    }
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
  }

  function disconnectWebSocket() {
    cleanup()
    if (websocket) {
      websocket.close(1000, "Intentional disconnect")
      websocket = null
    }
    isConnected.value = false
  }

  function reset() {
    disconnectWebSocket()
    notifications.value = []
    unreadCount.value = 0
    total.value = 0
    error.value = null
  }

  return {
    // State
    notifications,
    unreadCount,
    total,
    isLoading,
    isConnected,
    error,
    soundEnabled,
    // Computed
    hasUnread,
    displayCount,
    // Actions
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    connectWebSocket,
    disconnectWebSocket,
    reset,
    toggleSound,
  }
})
