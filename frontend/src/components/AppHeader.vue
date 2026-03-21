<template>
    <header class="app-header">
        <nav class="navbar">
            <div class="nav-brand">
                <router-link to="/" class="brand-link">
                    <img src="/logo.png" alt="Dhisppo" class="brand-logo" />
                    <span class="brand-text">Dhisppo</span>
                </router-link>
            </div>

            <div class="nav-links">
                <template v-if="isAuthenticated">
                    <div class="nav-link-container">
                        <router-link to="/notifications" class="nav-link">
                            <span>🔔</span>
                            <span
                                v-if="unreadCount && unreadCount > 0"
                                class="notification-badge"
                                >{{ unreadCount }}</span
                            >
                        </router-link>
                    </div>
                </template>

                <router-link to="/" class="nav-link">Home</router-link>

                <template v-if="isAuthenticated">
                    <router-link to="/events" class="nav-link"
                        >Events</router-link
                    >
                    
                    <router-link
                        v-if="isOrganizer || isAdmin"
                        to="/organizer"
                        class="nav-link"
                        >Organizer</router-link
                    >
                    <router-link v-if="isAdmin" to="/admin" class="nav-link"
                        >Admin</router-link
                    >

                    <div class="user-menu">
                        <router-link to="/profile" class="user-profile-link">
                            <div class="user-avatar">
                                {{ user?.username?.charAt(0).toUpperCase() }}
                            </div>
                            <div class="user-dropdown">
                                <span class="user-name">{{ user?.username }}</span>
                                <span class="user-role">{{ user?.role }}</span>
                            </div>
                        </router-link>
                        <button @click="logout" class="logout-btn">
                            Logout
                        </button>
                    </div>
                </template>

                <template v-else>
                    <router-link to="/login" class="nav-link"
                        >Login</router-link
                    >
                    <router-link
                        to="/register"
                        class="nav-link nav-link-primary"
                        >Sign Up</router-link
                    >
                </template>
            </div>
        </nav>
    </header>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useNotificationStore } from "@/stores/notifications";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const router = useRouter();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.isAdmin);
const isOrganizer = computed(() => authStore.isOrganizer);
const user = computed(() => authStore.user);
const unreadCount = computed(() => notificationStore.unreadCount);

const logout = () => {
    authStore.logout();
    router.push("/login");
};

onMounted(async () => {
    if (isAuthenticated.value) {
        try {
            // Set current user ID for proper filtering
            if (authStore.user?.id) {
                notificationStore.setCurrentUserId(authStore.user.id);
            }
            await notificationStore.fetchUnreadCount();
            notificationStore.startPolling();
        } catch (error) {
            console.error("Error fetching unread count:", error);
            if (error.response?.status === 403) {
                await authStore.initialize();
            }
        }
    }
});

onUnmounted(() => {
    notificationStore.stopPolling();
});

watch(isAuthenticated, async (newValue) => {
    if (newValue) {
        try {
            if (authStore.user?.id) {
                notificationStore.setCurrentUserId(authStore.user.id);
            }
            await notificationStore.fetchUnreadCount();
            notificationStore.startPolling();
        } catch (error) {
            console.error(
                "Error setting up notifications after auth change:",
                error,
            );
        }
    } else {
        notificationStore.stopPolling();
    }
});

watch(user, (newUser) => {
    if (newUser?.id && isAuthenticated.value) {
        notificationStore.setCurrentUserId(newUser.id);
    }
});

// Handle page visibility changes to optimize polling
const handleVisibilityChange = () => {
    if (document.hidden) {
        notificationStore.stopPolling();
    } else if (isAuthenticated.value) {
        notificationStore.fetchUnreadCount();
        notificationStore.startPolling();
    }
};

onMounted(() => {
    document.addEventListener("visibilitychange", handleVisibilityChange);
});

onUnmounted(() => {
    document.removeEventListener("visibilitychange", handleVisibilityChange);
});
</script>

<style scoped>
.app-header {
    background: var(--white);
    border-bottom: 1px solid var(--gray-200);
    padding: 0;
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 0;
    z-index: 50;
}

.navbar {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 1.5rem;
    height: 4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand .brand-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    transition: opacity 0.2s ease;
}

.nav-brand .brand-link:hover {
    opacity: 0.8;
}

.brand-logo {
    height: 32px;
    width: auto;
}

.brand-icon {
    font-size: 1.5rem;
}

.brand-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--primary-600);
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.nav-link {
    color: var(--gray-600);
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: var(--radius-md);
    font-weight: 500;
    transition: all 0.2s ease;
    position: relative;
}

.nav-link:hover {
    color: var(--primary-600);
    background-color: var(--gray-100);
}

.nav-link.router-link-active {
    color: var(--primary-600);
    background-color: var(--primary-50);
}

.nav-link-primary {
    background-color: var(--primary-600);
    color: var(--white);
}

.nav-link-primary:hover {
    background-color: var(--primary-700);
    color: var(--white);
}

.nav-link-container {
    position: relative;
}

.notification-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    background: #ef4444;
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 10px;
    min-width: 18px;
    text-align: center;
    line-height: 1;
}

.user-menu {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-left: 1rem;
    border-left: 1px solid var(--gray-200);
}

.user-profile-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
    transition: opacity 0.2s ease;
}

.user-profile-link:hover {
    opacity: 0.8;
}

.user-avatar {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
    color: var(--white);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
}

.user-dropdown {
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
}

.user-name {
    font-weight: 600;
    color: var(--gray-900);
    font-size: 0.875rem;
}

.user-role {
    font-size: 0.75rem;
    color: var(--gray-500);
    text-transform: capitalize;
}

.logout-btn {
    background-color: transparent;
    color: var(--gray-600);
    border: 1px solid var(--gray-300);
    padding: 0.375rem 0.75rem;
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.logout-btn:hover {
    background-color: var(--gray-100);
    color: var(--gray-800);
    border-color: var(--gray-400);
}

@media (max-width: 768px) {
    .navbar {
        padding: 0 1rem;
    }

    .nav-links {
        gap: 0.25rem;
    }

    .nav-link {
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
    }

    .user-dropdown {
        display: none;
    }

    .user-menu {
        gap: 0.5rem;
        padding-left: 0.5rem;
    }
}

@media (max-width: 640px) {
    .brand-text {
        display: none;
    }

    .nav-links {
        gap: 0.125rem;
    }

    .nav-link {
        padding: 0.5rem 0.5rem;
        font-size: 0.8rem;
    }
}
</style>
