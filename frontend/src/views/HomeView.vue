<template>
    <div class="home-container">
        <div class="hero-section">
            <div class="hero-content">
                <div class="hero-badge">
                    <span class="badge-icon">🎯</span>
                    <span class="badge-text">Event Management Platform</span>
                </div>
                
                <h1 class="hero-title">
                    Create Memorable
                    <span class="hero-title-gradient">Events</span>
                </h1>
                
                <p class="hero-subtitle">
                    The modern way to plan, organize, and track your events. 
                    From intimate gatherings to large celebrations.
                </p>

                <div class="cta-section">
                    <template v-if="isAuthenticated">
                        <router-link to="/events" class="cta-btn primary">
                            <span>Explore Events</span>
                            <span class="btn-arrow">→</span>
                        </router-link>
                        <router-link v-if="isAdmin" to="/admin" class="cta-btn secondary">
                            Admin Dashboard
                        </router-link>
                    </template>
                    <template v-else>
                        <router-link to="/register" class="cta-btn primary">
                            <span>Start Creating</span>
                            <span class="btn-arrow">→</span>
                        </router-link>
                        <router-link to="/login" class="cta-btn secondary">
                            Sign In
                        </router-link>
                    </template>
                </div>
            </div>
            
            <div class="hero-visual">
                <div class="floating-card card-1">
                    <div class="card-icon">📅</div>
                    <div class="card-text">Event Planning</div>
                </div>
                <div class="floating-card card-2">
                    <div class="card-icon">👥</div>
                    <div class="card-text">Guest Management</div>
                </div>
                <div class="floating-card card-3">
                    <div class="card-icon">📊</div>
                    <div class="card-text">Analytics</div>
                </div>
            </div>
        </div>

        <div class="features-section">
            <div class="features-container">
                <h2 class="features-title">Everything You Need</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🎨</div>
                        <h3>Beautiful Design</h3>
                        <p>Modern, intuitive interface that makes event planning a pleasure.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <h3>Lightning Fast</h3>
                        <p>Quick setup and real-time updates keep you in control.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔒</div>
                        <h3>Secure & Reliable</h3>
                        <p>Your data is protected with enterprise-grade security.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.isAdmin);
</script>

<style scoped>
.home-container {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--primary-50) 0%, var(--white) 100%);
}

.hero-section {
    padding: 6rem 1.5rem 4rem;
    max-width: 1280px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
    position: relative;
}

.hero-content {
    animation: fadeInUp 0.8s ease-out;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--primary-100);
    color: var(--primary-700);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-xl);
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 2rem;
    border: 1px solid var(--primary-200);
}

.badge-icon {
    font-size: 1rem;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1.1;
    color: var(--gray-900);
    margin-bottom: 1.5rem;
}

.hero-title-gradient {
    background: linear-gradient(135deg, var(--primary-600), var(--primary-400));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    font-size: 1.25rem;
    color: var(--gray-600);
    margin-bottom: 3rem;
    line-height: 1.6;
    max-width: 500px;
}

.cta-section {
    display: flex;
    gap: 1rem;
    align-items: center;
    flex-wrap: wrap;
}

.cta-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    border-radius: var(--radius-lg);
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s ease;
    border: 2px solid transparent;
    font-size: 1rem;
}

.cta-btn.primary {
    background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
    color: var(--white);
    box-shadow: var(--shadow-md);
}

.cta-btn.primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.btn-arrow {
    transition: transform 0.2s ease;
}

.cta-btn.primary:hover .btn-arrow {
    transform: translateX(2px);
}

.cta-btn.secondary {
    background-color: transparent;
    color: var(--primary-600);
    border-color: var(--primary-200);
}

.cta-btn.secondary:hover {
    background-color: var(--primary-50);
    border-color: var(--primary-300);
}

.hero-visual {
    position: relative;
    height: 400px;
    animation: fadeInUp 0.8s ease-out 0.2s both;
}

.floating-card {
    position: absolute;
    background: var(--white);
    padding: 1.5rem;
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
    display: flex;
    align-items: center;
    gap: 1rem;
    min-width: 180px;
    transition: transform 0.3s ease;
}

.floating-card:hover {
    transform: translateY(-4px);
}

.card-1 {
    top: 20px;
    right: 20px;
    animation: float 6s ease-in-out infinite;
}

.card-2 {
    top: 120px;
    left: 40px;
    animation: float 6s ease-in-out infinite 2s;
}

.card-3 {
    bottom: 60px;
    right: 60px;
    animation: float 6s ease-in-out infinite 4s;
}

.card-icon {
    font-size: 1.5rem;
}

.card-text {
    font-weight: 600;
    color: var(--gray-800);
}

.features-section {
    background: var(--white);
    padding: 5rem 1.5rem;
}

.features-container {
    max-width: 1200px;
    margin: 0 auto;
}

.features-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--gray-900);
    margin-bottom: 3rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2rem;
}

.feature-card {
    text-align: center;
    padding: 2.5rem;
    background: var(--gray-50);
    border-radius: var(--radius-xl);
    border: 1px solid var(--gray-200);
    transition: all 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--primary-200);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1.5rem;
}

.feature-card h3 {
    color: var(--gray-900);
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.feature-card p {
    color: var(--gray-600);
    line-height: 1.6;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes float {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-20px);
    }
}

@media (max-width: 1024px) {
    .hero-section {
        grid-template-columns: 1fr;
        gap: 3rem;
        text-align: center;
    }

    .hero-visual {
        height: 300px;
        order: -1;
    }

    .floating-card {
        position: static;
        margin: 0 auto 1rem;
        width: fit-content;
    }

    .card-1, .card-2, .card-3 {
        animation: none;
    }
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }

    .hero-subtitle {
        font-size: 1.125rem;
    }

    .cta-section {
        flex-direction: column;
        align-items: center;
    }

    .cta-btn {
        width: 200px;
        justify-content: center;
    }

    .features-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .hero-section {
        padding: 4rem 1rem 2rem;
    }

    .hero-title {
        font-size: 2rem;
    }

    .hero-badge {
        font-size: 0.75rem;
        padding: 0.375rem 0.75rem;
    }
}
</style>
