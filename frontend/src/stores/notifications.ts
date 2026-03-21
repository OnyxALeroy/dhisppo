import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { Notification, NotificationCreate } from "@/types";
import { notificationsAPI } from "@/utils/api";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_BASE_URL = API_BASE_URL.replace("http://", "ws://").replace("https://", "wss://");

export const useNotificationStore = defineStore("notifications", () => {
  const notifications = ref<Notification[]>([]);
  const unreadCount = ref<number>(0);
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);
  const pollingInterval = ref<NodeJS.Timeout | null>(null);
  const currentUserId = ref<string | null>(null);
  const wsConnection = ref<WebSocket | null>(null);
  const wsConnected = ref<boolean>(false);

  const connectWebSocket = (token: string) => {
    if (wsConnection.value?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(`${WS_BASE_URL}/notifications/ws?token=${token}`);

    ws.onopen = () => {
      wsConnected.value = true;
      console.log("WebSocket connected");
      stopPolling();
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === "notification") {
          const notification = message.data as Notification;
          notifications.value.unshift(notification);
          if (!notification.read && notification.receiver_id === currentUserId.value) {
            unreadCount.value += 1;
          }
        }
      } catch (e) {
        console.error("Error parsing WebSocket message:", e);
      }
    };

    ws.onclose = () => {
      wsConnected.value = false;
      console.log("WebSocket disconnected");
      startPolling();
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      wsConnected.value = false;
      startPolling();
    };

    wsConnection.value = ws;
  };

  const disconnectWebSocket = () => {
    if (wsConnection.value) {
      wsConnection.value.close();
      wsConnection.value = null;
      wsConnected.value = false;
    }
  };

  const setCurrentUserId = (userId: string) => {
    currentUserId.value = userId;
  };

  const receivedNotifications = computed(() => {
    if (!currentUserId.value) return [];
    return notifications.value.filter(n => n.receiver_id === currentUserId.value);
  });

  const sentNotifications = computed(() => {
    if (!currentUserId.value) return [];
    return notifications.value.filter(n => n.sender_id === currentUserId.value);
  });

  const unreadNotifications = computed(() => 
    receivedNotifications.value.filter(n => !n.read)
  );

  const readNotifications = computed(() => 
    receivedNotifications.value.filter(n => n.read)
  );

  const fetchNotifications = async (skip = 0, limit = 100, unreadOnly = false) => {
    loading.value = true;
    error.value = null;
    try {
      const fetchedNotifications = await notificationsAPI.getNotifications(skip, limit, unreadOnly);
      if (unreadOnly) {
        // If fetching only unread, merge with existing read notifications
        const existingRead = notifications.value.filter(n => n.read);
        notifications.value = [...fetchedNotifications, ...existingRead];
      } else {
        notifications.value = fetchedNotifications;
      }
    } catch (err) {
      error.value = "Failed to fetch notifications";
      console.error("Error fetching notifications:", err);
    } finally {
      loading.value = false;
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const count = await notificationsAPI.getUnreadCount();
      unreadCount.value = count.unread_count;
    } catch (err) {
      console.error("Error fetching unread count:", err);
    }
  };

  // Calculate local unread count (excluding sent notifications)
  const calculateUnreadCount = computed(() => {
    if (!currentUserId.value) return 0;
    return unreadNotifications.value.length;
  });

  const createNotification = async (notification: NotificationCreate) => {
    loading.value = true;
    error.value = null;
    try {
      const newNotification = await notificationsAPI.createNotification(notification);
      notifications.value.unshift(newNotification);
      // Only increment unread count if this is a received notification
      if (newNotification.receiver_id === currentUserId.value) {
        unreadCount.value += 1;
      }
      return newNotification;
    } catch (err) {
      error.value = "Failed to create notification";
      console.error("Error creating notification:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      const updatedNotification = await notificationsAPI.markAsRead(notificationId);
      const index = notifications.value.findIndex(n => n.id === notificationId);
      if (index !== -1) {
        const wasRead = notifications.value[index].read;
        notifications.value[index] = updatedNotification;
        // Only decrement unread count if this was a received notification and was unread
        if (!wasRead && notifications.value[index].receiver_id === currentUserId.value) {
          unreadCount.value = Math.max(0, unreadCount.value - 1);
        }
      }
      return updatedNotification;
    } catch (err) {
      error.value = "Failed to mark notification as read";
      console.error("Error marking notification as read:", err);
      throw err;
    }
  };

  const markAllAsRead = async () => {
    try {
      await notificationsAPI.markAllAsRead();
      notifications.value.forEach(notification => {
        notification.read = true;
      });
      unreadCount.value = 0;
    } catch (err) {
      error.value = "Failed to mark all notifications as read";
      console.error("Error marking all notifications as read:", err);
      throw err;
    }
  };

  const deleteNotification = async (notificationId: string) => {
    try {
      await notificationsAPI.deleteNotification(notificationId);
      const index = notifications.value.findIndex(n => n.id === notificationId);
      if (index !== -1) {
        const notification = notifications.value[index];
        // Only decrement unread count if this was a received notification and was unread
        if (!notification.read && notification.receiver_id === currentUserId.value) {
          unreadCount.value = Math.max(0, unreadCount.value - 1);
        }
        notifications.value.splice(index, 1);
      }
    } catch (err) {
      error.value = "Failed to delete notification";
      console.error("Error deleting notification:", err);
      throw err;
    }
  };

  const startPolling = () => {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value);
    }
    
    // Poll every 3 seconds for new unread notifications
    pollingInterval.value = setInterval(async () => {
      try {
        await fetchUnreadCount();
      } catch (error) {
        console.error('Error polling unread count:', error);
      }
    }, 3000);
  };

  const stopPolling = () => {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value);
      pollingInterval.value = null;
    }
  };

  const initialize = async () => {
    try {
      await Promise.all([
        fetchNotifications(),
        fetchUnreadCount()
      ]);
    } catch (error) {
      console.error('Error initializing notifications:', error);
    }
  };

  const initializeWithWebSocket = (token: string) => {
    initialize();
    connectWebSocket(token);
  };

  return {
    notifications,
    unreadCount,
    loading,
    error,
    wsConnected,
    unreadNotifications,
    readNotifications,
    receivedNotifications,
    sentNotifications,
    calculateUnreadCount,
    fetchNotifications,
    fetchUnreadCount,
    createNotification,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    initialize,
    initializeWithWebSocket,
    connectWebSocket,
    disconnectWebSocket,
    startPolling,
    stopPolling,
    setCurrentUserId,
  };
});