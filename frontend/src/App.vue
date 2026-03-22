<template>
    <div id="app">
        <AppHeader />
        <main class="main-content">
            <router-view />
        </main>
    </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import AppHeader from "@/components/AppHeader.vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

onMounted(async () => {
    await authStore.initialize();
});
</script>

<style lang="scss">
@import "@/assets/styles/main.scss";
</style>
