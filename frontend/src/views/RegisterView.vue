<template>
    <div class="register-container">
        <div class="register-card">
            <h1 class="register-title">Create Account</h1>
            <p class="register-subtitle">
                Join us to organize your New Year's resolutions
            </p>

            <form @submit.prevent="handleRegister" class="register-form">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input
                        id="username"
                        v-model="form.username"
                        type="text"
                        required
                        class="form-input"
                        placeholder="Choose a username"
                    />
                </div>

                <div class="form-group">
                    <label for="email">Email</label>
                    <input
                        id="email"
                        v-model="form.email"
                        type="email"
                        required
                        class="form-input"
                        placeholder="Enter your email"
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
                        placeholder="Create a password"
                    />
                </div>

                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <button type="submit" :disabled="loading" class="register-btn">
                    <span v-if="loading">Creating account...</span>
                    <span v-else>Create Account</span>
                </button>
            </form>

            <div class="register-footer">
                <p>
                    Already have an account?
                    <router-link to="/login" class="link"
                        >Sign in here</router-link
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
    email: "",
    password: "",
});

const loading = ref(false);
const error = ref("");

const handleRegister = async () => {
    loading.value = true;
    error.value = "";

    try {
        await authStore.register(form.username, form.email, form.password);
        await authStore.login(form.username, form.password);
        router.push("/resolutions");
    } catch (err: any) {
        error.value =
            err.response?.data?.detail ||
            "Registration failed. Please try again.";
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.register-container {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--primary-50) 0%, var(--white) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    position: relative;
    overflow: hidden;
}

.register-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 20% 80%, rgba(168, 85, 247, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
    pointer-events: none;
}

.register-card {
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

.register-title {
    color: var(--gray-900);
    font-size: 1.875rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-align: center;
}

.register-subtitle {
    color: var(--gray-600);
    text-align: center;
    margin-bottom: 2rem;
    font-size: 0.875rem;
}

.register-form {
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

.form-input {
    width: 100%;
    padding: 0.875rem 1rem;
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

.register-btn {
    background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
    color: var(--white);
    border: none;
    padding: 0.875rem;
    border-radius: var(--radius-lg);
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: 0.5rem;
}

.register-btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: var(--shadow-lg);
}

.register-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.register-footer {
    text-align: center;
    margin-top: 2rem;
    color: var(--gray-600);
    font-size: 0.875rem;
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

@media (max-width: 640px) {
    .register-container {
        padding: 1rem;
    }

    .register-card {
        padding: 2rem;
    }

    .register-title {
        font-size: 1.5rem;
    }
}
</style>
