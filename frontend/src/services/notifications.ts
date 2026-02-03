import api from "./api"

export interface Notification {
  id: string
  type: "info" | "success" | "warning" | "error"
  title: string
  message: string | null
  link: string | null
  is_read: boolean
  extra_data: Record<string, unknown> | null
  created_at: string
  read_at: string | null
}

export interface NotificationListResponse {
  notifications: Notification[]
  unread_count: number
  total: number
}

export interface WebSocketMessage {
  event: "connected" | "new_notification" | "notification_count" | "notification_read"
  data: Record<string, unknown>
}

export const notificationService = {
  async getNotifications(params?: {
    limit?: number
    offset?: number
    unread_only?: boolean
  }): Promise<NotificationListResponse> {
    const { data } = await api.get<NotificationListResponse>("/notifications/", {
      params,
    })
    return data
  },

  async getUnreadCount(): Promise<{ unread_count: number }> {
    const { data } = await api.get<{ unread_count: number }>("/notifications/unread-count")
    return data
  },

  async markAsRead(notificationIds: string[]): Promise<{ updated: number; unread_count: number }> {
    const { data } = await api.post<{ updated: number; unread_count: number }>(
      "/notifications/mark-read",
      { notification_ids: notificationIds }
    )
    return data
  },

  async markAllAsRead(): Promise<{ updated: number; unread_count: number }> {
    const { data } = await api.post<{ updated: number; unread_count: number }>(
      "/notifications/mark-all-read"
    )
    return data
  },
}
