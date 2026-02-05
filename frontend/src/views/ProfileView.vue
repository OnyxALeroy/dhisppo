<template>
    <div class="profile-container">
        <div class="profile-header">
            <h1>My Profile</h1>
            <div class="user-info-card">
                <div class="user-avatar">
                    <div class="avatar-circle">
                        {{ user?.username?.charAt(0).toUpperCase() }}
                    </div>
                </div>
                <div class="user-details">
                    <h2>{{ user?.username }}</h2>
                    <p class="user-email">{{ user?.email }}</p>
                    <p class="user-role">
                        <span :class="['role-badge', user?.role]">{{
                            user?.role
                        }}</span>
                    </p>
                    <p class="user-joined">
                        Joined: {{ formatDate(user?.created_at) }}
                    </p>
                </div>
            </div>
        </div>

        <div class="profile-content">
            <div class="payment-summary">
                <h3>Payment Summary</h3>
                <div class="summary-cards">
                    <div class="summary-card total-given">
                        <div class="card-icon">💸</div>
                        <div class="card-content">
                            <div class="card-label">Total Given</div>
                            <div class="card-amount">
                                ${{ paymentSummaryLoading ? '0.00' : (paymentSummary?.total_given || 0).toFixed(2) }}
                            </div>
                        </div>
                    </div>

                    <div class="summary-card total-received">
                        <div class="card-icon">💰</div>
                        <div class="card-content">
                            <div class="card-label">Total Received</div>
                            <div class="card-amount">
                                ${{ paymentSummaryLoading ? '0.00' : (paymentSummary?.total_received || 0).toFixed(2) }}
                            </div>
                        </div>
                    </div>

                    <div class="summary-card total-spent">
                        <div class="card-icon">🛒</div>
                        <div class="card-content">
                            <div class="card-label">Total Spent</div>
                            <div class="card-amount">
                                ${{ expenditureSummaryLoading ? '0.00' : (expenditureSummary?.total_spent || 0).toFixed(2) }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="my-events">
                <h3>My Events ({{ userEvents.length }})</h3>
                <div v-if="loading" class="loading">Loading events...</div>
                <div v-else-if="error" class="error">{{ error }}</div>
                <div v-else-if="userEvents.length === 0" class="empty-state">
                    <h4>No events yet</h4>
                    <p>You haven't participated in any events yet.</p>
                    <router-link to="/events" class="browse-events-btn">
                        Browse Events
                    </router-link>
                </div>
                <div v-else class="events-grid">
                    <div
                        v-for="event in userEvents"
                        :key="event.id"
                        class="event-card"
                    >
                        <div class="event-header">
                            <h4>{{ event.description }}</h4>
                            <div class="event-badges">
                                <span
                                    v-if="
                                        event.organizers.includes(
                                            user?.username,
                                        )
                                    "
                                    class="badge organizer"
                                >
                                    Organizer
                                </span>
                                <span class="badge participant"
                                    >Participant</span
                                >
                            </div>
                        </div>

                        <div class="event-details">
                            <div class="detail-row">
                                <span class="detail-label">📍 Locations:</span>
                                <div class="detail-value tags">
                                    <span
                                        v-for="location in event.locations"
                                        :key="location"
                                        class="tag"
                                    >
                                        {{ location }}
                                    </span>
                                </div>
                            </div>

                            <div class="detail-row">
                                <span class="detail-label">📅 Dates:</span>
                                <div class="detail-value dates">
                                    <div class="date-item">
                                        From: {{ formatDate(event.start_date) }}
                                        {{ formatTime(event.start_time) }}
                                    </div>
                                    <div
                                        v-if="event.end_date"
                                        class="date-item"
                                    >
                                        To: {{ formatDate(event.end_date) }}
                                        <span v-if="event.end_time">{{
                                            formatTime(event.end_time)
                                        }}</span>
                                    </div>
                                </div>
                            </div>

                            <div
                                v-if="getUserParticipant(event)"
                                class="payment-info"
                            >
                                <div class="payment-row">
                                    <span>Due:</span>
                                    <span class="amount due"
                                        >${{
                                            getUserParticipant(
                                                event,
                                            )?.due_payment.toFixed(2)
                                        }}</span
                                    >
                                </div>
                                <div class="payment-row">
                                    <span>Paid:</span>
                                    <span class="amount paid"
                                        >${{
                                            getUserParticipant(
                                                event,
                                            )?.paid_amount.toFixed(2)
                                        }}</span
                                    >
                                </div>
                            </div>

                            <div
                                v-if="
                                    getUserParticipant(event)?.tags.length > 0
                                "
                                class="dietary-tags"
                            >
                                <span class="detail-label">🍽️ Dietary:</span>
                                <div class="detail-value tags">
                                    <span
                                        v-for="tag in getUserParticipant(event)
                                            ?.tags"
                                        :key="tag"
                                        class="tag dietary"
                                    >
                                        {{ tag }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="event-footer">
                            <span class="event-date"
                                >Created:
                                {{ formatDate(event.created_at) }}</span
                            >
                            <button
                                @click="viewEventDetails(event)"
                                class="view-btn"
                            >
                                View Details
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Event Details Modal -->
        <div v-if="selectedEvent" class="modal-overlay" @click="closeDetails">
            <div class="modal details-modal" @click.stop>
                <div class="details-header">
                    <h2>{{ selectedEvent.description }}</h2>
                    <button @click="closeDetails" class="close-btn">×</button>
                </div>

                <div class="details-content">
                    <div class="detail-section">
                        <h3>📍 Locations</h3>
                        <div class="tags">
                            <span
                                v-for="location in selectedEvent.locations"
                                :key="location"
                                class="tag"
                            >
                                {{ location }}
                            </span>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h3>📅 Event Schedule</h3>
                        <div class="dates-list">
                            <div class="date-item">
                                <strong>Starts:</strong>
                                {{ formatDate(selectedEvent.start_date) }} at
                                {{ formatTime(selectedEvent.start_time) }}
                            </div>
                            <div
                                v-if="selectedEvent.end_date"
                                class="date-item"
                            >
                                <strong>Ends:</strong>
                                {{ formatDate(selectedEvent.end_date) }}
                                <span v-if="selectedEvent.end_time"
                                    >at
                                    {{
                                        formatTime(selectedEvent.end_time)
                                    }}</span
                                >
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h3>👥 Organizers</h3>
                        <div class="tags">
                            <span
                                v-for="organizer in selectedEvent.organizers"
                                :key="organizer"
                                class="tag"
                            >
                                {{ organizer }}
                            </span>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h3>🎫 Your Participation</h3>
                        <div
                            v-if="getUserParticipant(selectedEvent)"
                            class="user-participation"
                        >
                            <div class="participation-row">
                                <span>Amount Due:</span>
                                <span class="amount"
                                    >${{
                                        getUserParticipant(
                                            selectedEvent,
                                        )?.due_payment.toFixed(2)
                                    }}</span
                                >
                            </div>
                            <div class="participation-row">
                                <span>Amount Paid:</span>
                                <span class="amount"
                                    >${{
                                        getUserParticipant(
                                            selectedEvent,
                                        )?.paid_amount.toFixed(2)
                                    }}</span
                                >
                            </div>
                            <div class="participation-row">
                                <span>Remaining Balance:</span>
                                <span class="amount"
                                    >${{
                                        (
                                            getUserParticipant(selectedEvent)
                                                ?.due_payment -
                                            getUserParticipant(selectedEvent)
                                                ?.paid_amount
                                        ).toFixed(2)
                                    }}</span
                                >
                            </div>
                            <div
                                v-if="
                                    getUserParticipant(selectedEvent)?.tags
                                        .length > 0
                                "
                                class="dietary-info"
                            >
                                <span>Dietary Requirements:</span>
                                <div class="tags">
                                    <span
                                        v-for="tag in getUserParticipant(
                                            selectedEvent,
                                        )?.tags"
                                        :key="tag"
                                        class="tag dietary"
                                    >
                                        {{ tag }}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div v-else class="not-participating">
                            You are not participating in this event.
                        </div>
                    </div>

                    <div
                        v-if="selectedEvent.notes.length > 0"
                        class="detail-section"
                    >
                        <h3>📝 Notes</h3>
                        <ul class="notes-list">
                            <li v-for="note in selectedEvent.notes" :key="note">
                                {{ note }}
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useEventStore } from "@/stores/events";
import { paymentsAPI, expendituresAPI } from "@/utils/api";
import type { Event, Participant } from "@/types";

const authStore = useAuthStore();
const eventStore = useEventStore();

const user = computed(() => authStore.user);
const events = computed(() => eventStore.events);
const loading = computed(() => eventStore.loading);
const error = computed(() => eventStore.error);

const selectedEvent = ref<Event | null>(null);
const paymentSummary = ref<{ total_given: number; total_received: number } | null>(null);
const paymentSummaryLoading = ref(false);
const expenditureSummary = ref<{ total_spent: number } | null>(null);
const expenditureSummaryLoading = ref(false);

const userEvents = computed(() => {
    const username = user.value?.username;
    if (!username) return [];

    return events.value.filter(
        (event) =>
            event.participants.some(
                (participant) => participant.user_id === username,
            ) || event.organizers.includes(username),
    );
});

const getUserParticipant = (event: Event): Participant | undefined => {
    const username = user.value?.username;
    return event.participants.find(
        (participant) => participant.user_id === username,
    );
};

onMounted(async () => {
    try {
        await eventStore.fetchEvents();
        await Promise.all([
            fetchPaymentSummary(),
            fetchExpenditureSummary()
        ]);
    } catch (error) {
        console.error("Failed to fetch data:", error);
    }
});

const fetchPaymentSummary = async () => {
    try {
        paymentSummaryLoading.value = true;
        paymentSummary.value = await paymentsAPI.getMyPaymentSummary();
    } catch (error) {
        console.error("Failed to fetch payment summary:", error);
    } finally {
        paymentSummaryLoading.value = false;
    }
};

const fetchExpenditureSummary = async () => {
    try {
        expenditureSummaryLoading.value = true;
        expenditureSummary.value = await expendituresAPI.getMyExpenditureSummary();
    } catch (error) {
        console.error("Failed to fetch expenditure summary:", error);
    } finally {
        expenditureSummaryLoading.value = false;
    }
};

const viewEventDetails = (event: Event) => {
    selectedEvent.value = event;
};

const closeDetails = () => {
    selectedEvent.value = null;
};

const formatDate = (dateString: string | undefined) => {
    if (!dateString) return "";
    return new Date(dateString).toLocaleDateString();
};

const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
};

const formatTime = (timeString: string) => {
    if (!timeString) return "";
    // Handle both HH:MM and HH:MM:SS formats
    const [hours, minutes] = timeString.split(":");
    const time = new Date();
    time.setHours(parseInt(hours));
    time.setMinutes(parseInt(minutes));
    return time.toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
    });
};
</script>

<style scoped>
.profile-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.profile-header {
    margin-bottom: 2rem;
}

.profile-header h1 {
    color: #333;
    margin-bottom: 1.5rem;
}

.user-info-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 2rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 2rem;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.user-avatar {
    flex-shrink: 0;
}

.avatar-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: bold;
    border: 3px solid rgba(255, 255, 255, 0.3);
}

.user-details {
    flex: 1;
}

.user-details h2 {
    margin: 0 0 0.5rem 0;
    font-size: 1.8rem;
}

.user-email {
    margin: 0.25rem 0;
    opacity: 0.9;
    font-size: 1.1rem;
}

.user-role {
    margin: 0.5rem 0;
}

.role-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: capitalize;
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.user-joined {
    margin: 0.5rem 0 0 0;
    opacity: 0.8;
    font-size: 0.9rem;
}

.profile-content {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.payment-summary {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.payment-summary h3 {
    margin: 0 0 1.5rem 0;
    color: #333;
    font-size: 1.3rem;
}

.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
}

.summary-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    border-radius: 12px;
    border-left: 4px solid;
}

.summary-card.total-given {
    background: #fdf2f2;
    border-left-color: #e74c3c;
}

.summary-card.total-received {
    background: #f0fdf4;
    border-left-color: #27ae60;
}

.summary-card.total-spent {
    background: #fef3c7;
    border-left-color: #f59e0b;
}

.card-icon {
    font-size: 2rem;
}

.card-content {
    flex: 1;
}

.card-label {
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 0.25rem;
}

.card-amount {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
}

.my-events {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.my-events h3 {
    margin: 0 0 1.5rem 0;
    color: #333;
    font-size: 1.3rem;
}

.loading,
.error,
.empty-state {
    text-align: center;
    padding: 3rem;
    color: #666;
}

.error {
    color: #e74c3c;
    background-color: #fdf2f2;
    border-radius: 8px;
    border: 1px solid #f5c6cb;
}

.empty-state h4 {
    color: #333;
    margin-bottom: 0.5rem;
}

.browse-events-btn {
    display: inline-block;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    text-decoration: none;
    margin-top: 1rem;
    transition: transform 0.3s ease;
}

.browse-events-btn:hover {
    transform: translateY(-2px);
}

.events-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 1.5rem;
}

.event-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.5rem;
    border-left: 4px solid #667eea;
    transition: all 0.3s ease;
}

.event-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.event-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.event-header h4 {
    margin: 0;
    color: #333;
    font-size: 1.1rem;
    flex: 1;
}

.event-badges {
    display: flex;
    gap: 0.5rem;
}

.badge {
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

.badge.organizer {
    background: #e8f5e8;
    color: #27ae60;
}

.badge.participant {
    background: #e3f2fd;
    color: #1976d2;
}

.event-details {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.detail-row {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.detail-label {
    font-weight: 500;
    color: #555;
    font-size: 0.9rem;
}

.detail-value {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.tag {
    background: #e9ecef;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.8rem;
    color: #495057;
}

.tag.dietary {
    background: #fff3cd;
    color: #856404;
}

.dates {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.date-item {
    font-size: 0.85rem;
    color: #666;
    background: white;
    padding: 0.5rem;
    border-radius: 6px;
    border-left: 3px solid #667eea;
}

.more-dates {
    font-size: 0.8rem;
    color: #888;
    font-style: italic;
}

.payment-info {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e1e5e9;
}

.payment-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 0;
}

.amount {
    font-weight: 600;
}

.amount.due {
    color: #e74c3c;
}

.amount.paid {
    color: #27ae60;
}

.amount.paid-full {
    color: #27ae60;
}

.amount.partial {
    color: #f39c12;
}

.amount.unpaid {
    color: #e74c3c;
}

.dietary-tags {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.event-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e1e5e9;
}

.event-date {
    font-size: 0.85rem;
    color: #888;
}

.view-btn {
    background: #667eea;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.view-btn:hover {
    background: #5a6fd8;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal {
    background: white;
    border-radius: 12px;
    max-width: 700px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.details-modal {
    padding: 2rem;
}

.details-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.details-header h2 {
    margin: 0;
    color: #333;
}

.close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #666;
    padding: 0;
    width: 2rem;
    height: 2rem;
}

.close-btn:hover {
    color: #333;
}

.details-content {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.detail-section h3 {
    color: #333;
    margin: 0 0 0.75rem 0;
    font-size: 1.1rem;
}

.dates-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.user-participation {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e1e5e9;
}

.participation-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #e9ecef;
}

.participation-row:last-child {
    border-bottom: none;
}

.dietary-info {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e9ecef;
}

.not-participating {
    color: #666;
    font-style: italic;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.notes-list {
    margin: 0;
    padding-left: 1.5rem;
    color: #666;
}

.notes-list li {
    margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
    .profile-container {
        padding: 1rem;
    }

    .user-info-card {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }

    .summary-cards {
        grid-template-columns: 1fr;
    }

    .events-grid {
        grid-template-columns: 1fr;
    }

    .event-footer {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }

    .detail-row {
        gap: 0.25rem;
    }

    .payment-row {
        font-size: 0.9rem;
    }
}
</style>
