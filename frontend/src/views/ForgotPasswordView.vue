<template>
    <div class="forgot-container">
        <div class="forgot-card">
            <h1 class="forgot-title">Forgot Password</h1>
            <p class="forgot-subtitle">
                Enter your email address and we'll send you a link to reset your password.
            </p>

            <form @submit.prevent="handleSubmit" class="forgot-form">
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

                <div v-if="message" class="success-message">
                    {{ message }}
                </div>

                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <button type="submit" :disabled="loading" class="submit-btn">
                    <span v-if="loading">Sending...</span>
                    <span v-else>Send Reset Link</span>
                </button>
            </form>

            <div class="forgot-footer">
                <p>
                    Remember your password?
                    <router-link to="/login" class="link">Sign in</router-link>
                </p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { authAPI } from "@/utils/api";

const form = reactive({
    email: "",
});

const loading = ref(false);
const message = ref("");
const error = ref("");

const handleSubmit = async () => {
    loading.value = true;
    error.value = "";
    message.value = "";

    try {
        const response = await authAPI.forgotPassword(form.email);
        message.value = response.message;
    } catch (err: any) {
        error.value = err.response?.data?.detail || "Failed to send reset email";
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.forgot-container {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--primary-50) 0%, var(--white) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.forgot-card {
    background: var(--white);
    padding: 3rem;
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-xl);
    width: 100%;
    max-width: 420px;
    border: 1px solid var(--gray-200);
}

.forgot-title {
    color: var(--gray-900);
    font-size: 1.875rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-align: center;
}

.forgot-subtitle {
    color: var(--gray-600);
    text-align: center;
    margin-bottom: 2rem;
    font-size: 0.875rem;
}

.forgot-form {
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
}

.form-input:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
}

.success-message {
    color: #16a34a;
    background-color: #f0fdf4;
    padding: 0.75rem;
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    border: 1px solid #bbf7d0;
}

.error-message {
    color: #dc2626;
    background-color: #fef2f2;
    padding: 0.75rem;
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    border: 1px solid #fecaca;
}

.submit-btn {
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

.submit-btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: var(--shadow-lg);
}

.submit-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.forgot-footer {
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
</style>
