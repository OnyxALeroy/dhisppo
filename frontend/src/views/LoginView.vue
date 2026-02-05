<template>
    <div class="login-container">
        <div class="login-card">
            <h1 class="login-title">Welcome Back!</h1>
            <p class="login-subtitle">Sign in to access our Events!</p>

            <form @submit.prevent="handleLogin" class="login-form">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input
                        id="username"
                        v-model="form.username"
                        type="text"
                        required
                        class="form-input"
                        placeholder="Enter your username"
                    />
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input
                        id="password"
                        v-model="form.password"
                        type="password"
                        required
                        class="form-input"
                        placeholder="Enter your password"
                    />
                </div>

                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <button type="submit" :disabled="loading" class="login-btn">
                    <span v-if="loading">Signing in...</span>
                    <span v-else>Sign In</span>
                </button>
            </form>

            <div class="login-footer">
                <p>
                    Don't have an account?
                    <router-link to="/register" class="link"
                        >Register here</router-link
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
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.login-card {
    background: white;
    padding: 3rem;
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
}

.login-title {
    color: #333;
    font-size: 2rem;
    margin-bottom: 0.5rem;
    text-align: center;
}

.login-subtitle {
    color: #666;
    text-align: center;
    margin-bottom: 2rem;
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
    color: #333;
    font-weight: 500;
}

.form-input {
    padding: 0.75rem 1rem;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: #667eea;
}

.error-message {
    color: #e74c3c;
    background-color: #fdf2f2;
    padding: 0.75rem;
    border-radius: 8px;
    text-align: center;
    border: 1px solid #f5c6cb;
}

.login-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 1rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: transform 0.3s ease;
}

.login-btn:hover:not(:disabled) {
    transform: translateY(-2px);
}

.login-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.login-footer {
    text-align: center;
    margin-top: 2rem;
    color: #666;
}

.link {
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
}

.link:hover {
    text-decoration: underline;
}
</style>
