<template>
    <div class="login-container">
        <div class="login-background">
            <div class="bg-shape shape-1"></div>
            <div class="bg-shape shape-2"></div>
            <div class="bg-shape shape-3"></div>
        </div>

        <div class="login-card">
            <div class="login-header">
                <div class="login-logo">
                    <img src="/big-logo.png" alt="Dhisppo" class="logo-img" />
                </div>
                <h1 class="login-title">Welcome back</h1>
                <p class="login-subtitle">
                    Sign in to your account to continue
                </p>
            </div>

            <form @submit.prevent="handleLogin" class="login-form">
                <div class="form-group">
                    <label for="username">Username</label>
                    <div class="input-wrapper">
                        <span class="input-icon">👤</span>
                        <input
                            id="username"
                            v-model="form.username"
                            type="text"
                            required
                            class="form-input"
                            placeholder="Enter your username"
                        />
                    </div>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <div class="input-wrapper">
                        <span class="input-icon">🔒</span>
                        <input
                            id="password"
                            v-model="form.password"
                            type="password"
                            required
                            class="form-input"
                            placeholder="Enter your password"
                        />
                    </div>
                </div>

                <div v-if="error" class="error-message">
                    <span class="error-icon">⚠️</span>
                    {{ error }}
                </div>

                <button type="submit" :disabled="loading" class="login-btn">
                    <span v-if="loading" class="loading-spinner"></span>
                    <span v-else>Sign In</span>
                </button>
            </form>

            <div class="login-footer">
                <p>
                    New to Dhisppo?
                    <router-link to="/register" class="link"
                        >Create an account</router-link
                    >
                </p>
                <p class="forgot-link">
                    <router-link to="/forgot-password" class="link"
                        >Forgot password?</router-link
                    >
                </p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const form = reactive({
    username: "",
    password: "",
});

const loading = ref(false);
const error = ref("");

const handleLogin = async () => {
    loading.value = true;
    error.value = "";

    try {
        await authStore.login(form.username, form.password);
        router.push("/events");
    } catch (err: any) {
        error.value =
            err.response?.data?.detail || "Login failed. Please try again.";
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.login-container {
    min-height: 100vh;
    background: linear-gradient(
        135deg,
        var(--primary-50) 0%,
        var(--white) 100%
    );
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    position: relative;
    overflow: hidden;
}

.login-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
}

.bg-shape {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    background: linear-gradient(135deg, var(--primary-400), var(--primary-600));
}

.shape-1 {
    width: 300px;
    height: 300px;
    top: -150px;
    right: -100px;
    animation: float 8s ease-in-out infinite;
}

.shape-2 {
    width: 200px;
    height: 200px;
    bottom: -100px;
    left: -50px;
    animation: float 8s ease-in-out infinite 3s;
}

.shape-3 {
    width: 150px;
    height: 150px;
    top: 50%;
    right: 10%;
    animation: float 8s ease-in-out infinite 5s;
}

.login-card {
    background: var(--white);
    padding: 3rem;
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-xl);
    width: 100%;
    max-width: 420px;
    border: 1px solid var(--gray-200);
    position: relative;
    z-index: 10;
}

.login-header {
    text-align: center;
    margin-bottom: 1.5rem;
}

.login-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.logo-img {
    height: 200px;
    width: auto;
}

.logo-icon {
    font-size: 1.5rem;
}

.logo-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--primary-600);
}

.login-title {
    color: var(--gray-900);
    font-size: 1.875rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.login-subtitle {
    color: var(--gray-600);
    font-size: 0.875rem;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    color: var(--gray-700);
    font-weight: 500;
    font-size: 0.875rem;
}

.input-wrapper {
    position: relative;
}

.input-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1rem;
    color: var(--gray-400);
}

.form-input {
    width: 100%;
    padding: 0.875rem 1rem 0.875rem 2.5rem;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 0.875rem;
    transition: all 0.2s ease;
    background-color: var(--white);
}

.form-input:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
}

.form-input::placeholder {
    color: var(--gray-400);
}

.error-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #dc2626;
    background-color: #fef2f2;
    padding: 0.75rem;
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    border: 1px solid #fecaca;
}

.error-icon {
    font-size: 1rem;
}

.login-btn {
    background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
    color: var(--white);
    border: none;
    padding: 0.875rem;
    border-radius: var(--radius-lg);
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.login-btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: var(--shadow-lg);
}

.login-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
}

.login-footer {
    text-align: center;
    margin-top: 2rem;
    color: var(--gray-600);
    font-size: 0.875rem;
}

.forgot-link {
    margin-top: 1rem;
}

.link {
    color: var(--primary-600);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s ease;
}

.link:hover {
    color: var(--primary-700);
}

@keyframes float {
    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
    }
    50% {
        transform: translateY(-20px) rotate(5deg);
    }
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@media (max-width: 640px) {
    .login-container {
        padding: 1rem;
    }

    .login-card {
        padding: 2rem;
    }

    .login-title {
        font-size: 1.5rem;
    }

    .shape-1,
    .shape-2,
    .shape-3 {
        display: none;
    }
}
</style>
