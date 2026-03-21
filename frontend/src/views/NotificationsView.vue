<template>
  <div class="notifications-container">
    <div class="notifications-header">
      <div class="header-content">
        <h1 class="page-title">Notifications</h1>
        <div class="header-actions">
          <div v-if="notificationStore.unreadCount > 0" class="unread-badge">
            {{ notificationStore.unreadCount }} unread
          </div>
          <button 
            v-if="notificationStore.unreadNotifications.length > 0"
            @click="markAllAsRead"
            class="btn btn-secondary btn-sm"
            :disabled="notificationStore.loading"
          >
            Mark All as Read
          </button>
        </div>
      </div>
    </div>

    <div class="notifications-filters">
      <div class="filter-tabs">
        <button 
          @click="activeFilter = 'all'"
          :class="['filter-tab', { active: activeFilter === 'all' }]"
        >
          All ({{ notificationStore.receivedNotifications.length }})
        </button>
        <button 
          @click="activeFilter = 'unread'"
          :class="['filter-tab', { active: activeFilter === 'unread' }]"
        >
          Unread ({{ notificationStore.unreadNotifications.length }})
        </button>
        <button 
          @click="activeFilter = 'read'"
          :class="['filter-tab', { active: activeFilter === 'read' }]"
        >
          Read ({{ notificationStore.readNotifications.length }})
        </button>
        <button 
          @click="activeFilter = 'sent'"
          :class="['filter-tab', { active: activeFilter === 'sent' }]"
        >
          Sent ({{ notificationStore.sentNotifications.length }})
        </button>
      </div>
    </div>

    <div v-if="notificationStore.loading && notificationStore.notifications.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>Loading notifications...</p>
    </div>

    <div v-else-if="!notificationStore.loading && (!filteredNotifications || filteredNotifications.length === 0)" class="empty-state">
      <div class="empty-icon">📬</div>
      <h3>No notifications</h3>
      <p v-if="activeFilter === 'unread'">All caught up! No unread notifications.</p>
      <p v-else-if="activeFilter === 'sent'">You haven't sent any notifications yet.</p>
      <p v-else>Your notification inbox is empty.</p>
      <p v-if="!authStore.canSendNotifications && activeFilter === 'all'" class="permission-note">
        Only organizers and administrators can send notifications.
      </p>
    </div>

    <div v-else class="notifications-list">
      <div 
        v-for="notification in filteredNotifications"
        :key="notification.id"
        :class="['notification-item', { unread: !notification.read }]"
      >
        <div class="notification-content">
          <div class="notification-header">
            <div class="notification-sender">
              <strong v-if="activeFilter === 'sent'">To: {{ getReceiverName(notification.receiver_id) }}</strong>
              <strong v-else>{{ getSenderName(notification, notification.sender_id) }}</strong>
              <span class="notification-time">
                {{ formatTime(notification.created_at) }}
              </span>
            </div>
            <div class="notification-actions">
              <button 
                v-if="!notification.read && activeFilter !== 'sent'"
                @click="markAsRead(notification.id)"
                class="btn-icon"
                title="Mark as read"
              >
                ✓
              </button>
              <button 
                @click="deleteNotification(notification.id)"
                class="btn-icon btn-danger"
                title="Delete notification"
              >
                ×
              </button>
            </div>
          </div>
            <div class="notification-body">
            <p v-if="notification.content.startsWith('invite:')">
              <strong>{{ getInviteSender(notification) }}</strong> invited you to join: <strong>{{ getEventName(notification.content) }}</strong>
            </p>
            <p v-else>{{ notification.content }}</p>
            <button 
              v-if="isInviteNotification(notification) && activeFilter !== 'sent'"
              @click.stop="handleNotificationClick(notification)"
              class="btn btn-primary btn-sm accept-btn"
            >
              Accept & Join
            </button>
          </div>
        </div>
        <div v-if="!notification.read && activeFilter !== 'sent'" class="unread-indicator"></div>
      </div>
    </div>

    <!-- Send Notification Modal -->
    <div v-if="showSendModal" class="modal-overlay" @click="closeSendModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Send Notification</h2>
          <button @click="closeSendModal" class="btn-icon">×</button>
        </div>
        <form @submit.prevent="sendNotification" class="modal-body">
          <div class="form-group">
            <label for="receiver">Recipient Username:</label>
            <input 
              id="receiver" 
              v-model="newNotification.receiver_username" 
              type="text" 
              required
              placeholder="Enter recipient's username"
            />
            <small class="form-hint">Enter the exact username of the recipient</small>
          </div>
          <div class="form-group">
            <label for="content">Message:</label>
            <textarea 
              id="content" 
              v-model="newNotification.content" 
              rows="4" 
              required
              placeholder="Enter your notification message..."
            ></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeSendModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="sending">
              {{ sending ? 'Sending...' : 'Send Notification' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Floating Action Button (only for users with permission) -->
    <button 
      v-if="authStore.canSendNotifications"
      @click="openSendModal"
      class="fab"
      title="Send notification"
    >
      ✉️
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useNotificationStore } from '@/stores/notifications';
import { useAuthStore } from '@/stores/auth';
import { useEventStore } from '@/stores/events';
import { authAPI } from '@/utils/api';
import type { NotificationCreate } from '@/types';

const notificationStore = useNotificationStore();
const authStore = useAuthStore();
const eventStore = useEventStore();

const activeFilter = ref<'all' | 'unread' | 'read' | 'sent'>('all');
const showSendModal = ref(false);
const sending = ref(false);
const availableUsers = ref<any[]>([]);

const newNotification = ref<NotificationCreate & { receiver_username?: string }>({
  sender_id: '',
  receiver_id: '',
  receiver_username: '',
  content: ''
});

const filteredNotifications = computed(() => {
  switch (activeFilter.value) {
    case 'unread':
      return notificationStore.unreadNotifications;
    case 'read':
      return notificationStore.readNotifications;
    case 'sent':
      return notificationStore.sentNotifications;
    default:
      return notificationStore.receivedNotifications;
  }
});

const formatTime = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
};

const getSenderName = (notification: any, senderId: string) => {
  // First check if sender is current user
  if (authStore.user?.id === senderId) {
    return 'You';
  }
  // Then check sender_username from backend
  if (notification.sender_username && notification.sender_username !== 'Unknown') {
    return notification.sender_username;
  }
  // Fallback to available users list
  const user = availableUsers.value.find(u => u.id === senderId);
  if (user) return user.username;
  return 'Unknown User';
};

const getReceiverName = (receiverId: string) => {
  const user = availableUsers.value.find(u => u.id === receiverId);
  if (user) return user.username;
  if (authStore.user?.id === receiverId) return authStore.user.username;
  return 'Unknown User';
};

const getEventName = (content: string) => {
  // Format: invite:{event_id}:{event_name}:{sender_username}
  const parts = content.split(':');
  return parts.length >= 3 ? parts[2] : 'Unknown Event';
};

const getInviteSender = (notification: any) => {
  // First check if sender is current user
  if (authStore.user?.id === notification.sender_id) {
    return 'You';
  }
  // Then check sender_username from backend
  if (notification.sender_username && notification.sender_username !== 'Unknown') {
    return notification.sender_username;
  }
  // Fallback: parse from content format invite:{event_id}:{event_name}:{sender_username}
  const parts = notification.content.split(':');
  return parts.length >= 4 ? parts[3] : 'Someone';
};

const isInviteNotification = (notification: any) => {
  return notification.content.startsWith('invite:');
};

const markAsRead = async (notificationId: string) => {
  try {
    await notificationStore.markAsRead(notificationId);
  } catch (error) {
    console.error('Error marking notification as read:', error);
  }
};

const markAllAsRead = async () => {
  try {
    await notificationStore.markAllAsRead();
  } catch (error) {
    console.error('Error marking all notifications as read:', error);
  }
};

const deleteNotification = async (notificationId: string) => {
  try {
    await notificationStore.deleteNotification(notificationId);
  } catch (error) {
    console.error('Error deleting notification:', error);
  }
};

const handleNotificationClick = async (notification: any) => {
  // Check if this is an event invitation
  if (notification.content.startsWith('invite:')) {
    const parts = notification.content.split(':');
    if (parts.length >= 2) {
      const eventId = parts[1];
      try {
        await eventStore.acceptInvitation(eventId);
        // Try to mark as read, but don't fail if notification is already gone
        try {
          await notificationStore.markAsRead(notification.id);
        } catch (e) {
          console.warn('Could not mark notification as read:', e);
        }
        alert('You have joined the event!');
      } catch (error) {
        console.error('Error accepting invitation:', error);
        alert('Failed to join event. You may already be a participant.');
      }
      return;
    }
  }
  
  // Mark as read for non-invite notifications
  if (!notification.read) {
    await notificationStore.markAsRead(notification.id);
  }
};

const openSendModal = async () => {
  if (!authStore.isAuthenticated || !authStore.canSendNotifications) {
    return;
  }

  // Try to load users if not already loaded
  if (availableUsers.value.length === 0) {
    try {
      const users = await authAPI.getUsers();
      availableUsers.value = users.filter(u => u.id !== authStore.user?.id);
    } catch (error) {
      console.log('Users list not available, will use username input');
      // Don't fail the modal opening for organizers who can't access user list
    }
  }
  
  newNotification.value.sender_id = authStore.user?.id || '';
  showSendModal.value = true;
};

const closeSendModal = () => {
  showSendModal.value = false;
  newNotification.value = {
    sender_id: authStore.user?.id || '',
    receiver_id: '',
    receiver_username: '',
    content: ''
  };
};

const sendNotification = async () => {
  sending.value = true;
  try {
    // Find user by username if username is provided
    if (newNotification.value.receiver_username) {
      // Try to get users if not already loaded
      if (availableUsers.value.length === 0) {
        try {
          const users = await authAPI.getUsers();
          availableUsers.value = users;
        } catch (error) {
          console.error('Error fetching users for username lookup:', error);
          alert('Unable to verify recipient. Please contact an administrator.');
          return;
        }
      }
      
      const recipient = availableUsers.value.find(u => 
        u.username === newNotification.value.receiver_username
      );
      
      if (!recipient) {
        alert('User not found. Please check the username and try again.');
        return;
      }
      
      newNotification.value.receiver_id = recipient.id;
    }
    
    await notificationStore.createNotification(newNotification.value);
    closeSendModal();
  } catch (error) {
    console.error('Error sending notification:', error);
    alert('Failed to send notification. Please try again.');
  } finally {
    sending.value = false;
  }
};

onMounted(async () => {
  // Ensure user is authenticated before proceeding
  if (!authStore.isAuthenticated) {
    return;
  }

  try {
    // Set current user ID for filtering
    if (authStore.user?.id) {
      notificationStore.setCurrentUserId(authStore.user.id);
      
      // Initialize notifications first
      await notificationStore.initialize();
      
      // Try to load users, but don't fail if not authorized
      try {
        const users = await authAPI.getUsers();
        availableUsers.value = users;
      } catch (error) {
        console.log('Users list not available (normal for organizers)');
        // Don't fail the whole initialization for organizers
      }
      
      // Always include current user in the list for name resolution
      if (authStore.user && !availableUsers.value.find(u => u.id === authStore.user?.id)) {
        availableUsers.value.unshift({
          id: authStore.user.id,
          username: authStore.user.username,
          email: authStore.user.email,
          role: authStore.user.role
        });
      }
    }
  } catch (error) {
    console.error('Error initializing notifications view:', error);
    // If we get a 403, try to reinitialize auth
    if (error.response?.status === 403) {
      await authStore.initialize();
    }
  }
});
</script>

<style scoped>
.notifications-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.notifications-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.unread-badge {
  background: #ef4444;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.notifications-filters {
  margin-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 12px 16px;
  border: none;
  background: none;
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.filter-tab:hover {
  color: #374151;
}

.filter-tab.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.permission-note {
  font-size: 0.875rem;
  color: #9ca3af;
  font-style: italic;
  margin-top: 12px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  position: relative;
  transition: all 0.2s;
}

.notification-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.notification-item.unread {
  background: #f0f9ff;
  border-color: #3b82f6;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.notification-sender {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-time {
  font-size: 0.875rem;
  color: #6b7280;
}

.notification-actions {
  display: flex;
  gap: 8px;
}

.notification-body p {
  margin: 0;
  color: #374151;
  line-height: 1.5;
}

.accept-btn {
  margin-top: 8px;
}

.unread-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: #3b82f6;
  border-radius: 0 2px 2px 0;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 0.875rem;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  color: #374151;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #e5e7eb;
}

.btn-danger:hover {
  background: #fef2f2;
  color: #ef4444;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  color: #1f2937;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group select:focus,
.form-group textarea:focus,
.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-hint {
  display: block;
  margin-top: 4px;
  font-size: 0.75rem;
  color: #6b7280;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transition: all 0.2s;
  z-index: 100;
}

.fab:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

@media (max-width: 768px) {
  .notifications-container {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-tabs {
    overflow-x: auto;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>