<template>
    <div class="reset-container">
        <div class="reset-card">
            <h1 class="reset-title">Reset Password</h1>
            <p class="reset-subtitle">
                Enter your new password below.
            </p>

            <form @submit.prevent="handleSubmit" class="reset-form">
                <div class="form-group">
                    <label for="password">New Password</label>
                    <input
                        id="password"
                        v-model="form.password"
                        type="password"
                        required
                        minlength="8"
                        class="form-input"
                        placeholder="Enter new password"
                    />
                </div>

                <div class="form-group">
                    <label for="confirmPassword">Confirm Password</label>
                    <input
                        id="confirmPassword"
                        v-model="form.confirmPassword"
                        type="password"
                        required
                        class="form-input"
                        placeholder="Confirm new password"
                    />
                </div>

                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <div v-if="success" class="success-message">
                    {{ success }}
                </div>

                <button type="submit" :disabled="loading" class="submit-btn">
                    <span v-if="loading">Resetting...</span>
                    <span v-else>Reset Password</span>
                </button>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authAPI } from "@/utils/api";

const route = useRoute();
const router = useRouter();

const form = reactive({
    password: "",
    confirmPassword: "",
});

const loading = ref(false);
const error = ref("");
const success = ref("");

onMounted(() => {
    const token = route.query.token as string;
    if (!token) {
        error.value = "Invalid reset link. Please request a new one.";
    }
});

const handleSubmit = async () => {
    if (form.password !== form.confirmPassword) {
        error.value = "Passwords do not match";
        return;
    }

    if (form.password.length < 8) {
        error.value = "Password must be at least 8 characters";
        return;
    }

    const token = route.query.token as string;
    if (!token) {
        error.value = "Invalid reset link";
        return;
    }

    loading.value = true;
    error.value = "";
    success.value = "";

    try {
        await authAPI.resetPassword(token, form.password);
        success.value = "Password reset successfully!";
        setTimeout(() => {
            router.push("/login");
        }, 2000);
    } catch (err: any) {
        error.value = err.response?.data?.detail || "Failed to reset password";
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.reset-container {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--primary-50) 0%, var(--white) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.reset-card {
    background: var(--white);
    padding: 3rem;
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-xl);
    width: 100%;
    max-width: 420px;
    border: 1px solid var(--gray-200);
}

.reset-title {
    color: var(--gray-900);
    font-size: 1.875rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-align: center;
}

.reset-subtitle {
    color: var(--gray-600);
    text-align: center;
    margin-bottom: 2rem;
    font-size: 0.875rem;
}

.reset-form {
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
</style>
