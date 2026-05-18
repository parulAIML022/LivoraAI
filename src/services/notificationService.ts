import { apiRequest } from "@/lib/api";

export interface Notification {
  id: string;
  userId: string;
  title: string;
  message: string;
  type: string;
  metadata: Record<string, unknown>;
  read: boolean;
  createdAt: string;
}

export interface NotificationListResponse {
  items: Notification[];
  unreadCount: number;
}

export function getNotifications(limit = 20): Promise<NotificationListResponse> {
  return apiRequest<NotificationListResponse>(
    `/api/notifications?limit=${limit}`,
    { auth: true }
  );
}

export function getUnreadNotificationCount(): Promise<{ count: number }> {
  return apiRequest<{ count: number }>("/api/notifications/unread-count", {
    auth: true,
  });
}

export function markNotificationRead(id: string): Promise<Notification> {
  return apiRequest<Notification>(`/api/notifications/${id}/read`, {
    method: "PATCH",
    auth: true,
  });
}

export function markAllNotificationsRead(): Promise<{ marked: number }> {
  return apiRequest<{ marked: number }>("/api/notifications/read-all", {
    method: "PATCH",
    auth: true,
  });
}
