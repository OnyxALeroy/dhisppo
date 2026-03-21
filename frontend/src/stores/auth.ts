import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User, UserRole } from "@/types";
import { authAPI } from "@/utils/api";
import { useNotificationStore } from "./notifications";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem("access_token"));

  const isAuthenticated = computed(() => !!token.value && !!user.value && token.value !== "");
  const isAdmin = computed(() => user.value?.role === "admin");
  const isOrganizer = computed(() => user.value?.role === "organizer");
  const canCreateEvents = computed(() => isAdmin.value || isOrganizer.value);
  const canSendNotifications = computed(() => isAdmin.value || isOrganizer.value);

  const login = async (username: string, password: string) => {
    try {
      const response = await authAPI.login({ username, password });
      token.value = response.access_token;
      localStorage.setItem("access_token", response.access_token);

      await fetchCurrentUser();

      const notificationStore = useNotificationStore();
      notificationStore.connectWebSocket(response.access_token);

      return true;
    } catch (error) {
      logout();
      throw error;
    }
  };

  const register = async (
    username: string,
    email: string,
    password: string,
  ) => {
    try {
      const user = await authAPI.register({ username, email, password });
      return user;
    } catch (error) {
      throw error;
    }
  };

  const fetchCurrentUser = async () => {
    try {
      const currentUser = await authAPI.getCurrentUser();
      user.value = currentUser;
    } catch (error) {
      logout();
      throw error;
    }
  };

  const logout = () => {
    const notificationStore = useNotificationStore();
    notificationStore.disconnectWebSocket();
    user.value = null;
    token.value = null;
    localStorage.removeItem("access_token");
  };

  const initialize = async () => {
    if (token.value) {
      try {
        await fetchCurrentUser();
        const notificationStore = useNotificationStore();
        notificationStore.connectWebSocket(token.value);
      } catch (error) {
        logout();
      }
    }
  };

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    isOrganizer,
    canCreateEvents,
    canSendNotifications,
    login,
    register,
    logout,
    fetchCurrentUser,
    initialize,
  };
});
