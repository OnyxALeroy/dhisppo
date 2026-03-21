import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "Home",
      component: () => import("@/views/HomeView.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/login",
      name: "Login",
      component: () => import("@/views/LoginView.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/forgot-password",
      name: "ForgotPassword",
      component: () => import("@/views/ForgotPasswordView.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/reset-password",
      name: "ResetPassword",
      component: () => import("@/views/ResetPasswordView.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/register",
      name: "Register",
      component: () => import("@/views/RegisterView.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/events",
      name: "Events",
      component: () => import("@/views/EventsView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/organizer",
      name: "Organizer",
      component: () => import("@/views/OrganizerView.vue"),
      meta: { requiresAuth: true, requiresOrganizer: true },
    },
    {
      path: "/event/:id",
      name: "EventDetail",
      component: () => import("@/views/EventDetailView.vue"),
      meta: { requiresAuth: true, requiresOrganizer: true },
    },
    {
      path: "/admin",
      name: "Admin",
      component: () => import("@/views/AdminView.vue"),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: "/profile",
      name: "Profile",
      component: () => import("@/views/ProfileView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/notifications",
      name: "Notifications",
      component: () => import("@/views/NotificationsView.vue"),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchCurrentUser();
    } catch (error) {
      authStore.logout();
      if (to.meta.requiresAuth) {
        next("/login");
        return;
      }
    }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/login");
    return;
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next("/events");
    return;
  }

  if (to.meta.requiresOrganizer && !authStore.isOrganizer && !authStore.isAdmin) {
    next("/events");
    return;
  }

  if (
    (to.name === "Login" || to.name === "Register") &&
    authStore.isAuthenticated
  ) {
    next("/events");
    return;
  }

  next();
});

export default router;
