<template>
    <div class="events-container">
        <div class="events-header">
            <h1>Events</h1>
            <div class="header-actions">
                <div class="filters">
                    <input
                        v-model="filterOrganizer"
                        placeholder="Filter by organizer..."
                        class="filter-input"
                    />
                    <input
                        v-model="filterLocation"
                        placeholder="Filter by location..."
                        class="filter-input"
                    />
                    <select v-model="filterVisibility" class="filter-input">
                        <option value="">All Events</option>
                        <option value="public">Public Only</option>
                        <option value="private">Private Only</option>
                    </select>
                </div>
                <button
                    v-if="authStore.canCreateEvents"
                    @click="openCreateModal"
                    class="create-btn"
                >
                    + Create Event
                </button>
            </div>
        </div>

        <div v-if="loading" class="loading">Loading events...</div>

        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else-if="filteredEvents.length === 0" class="empty-state">
            <h3>No events found</h3>
            <p v-if="filterOrganizer || filterLocation || filterVisibility">
                Try adjusting your filters or
                <button @click="clearFilters" class="clear-filters">
                    clear them
                </button>
            </p>
            <p v-else>Start by creating the first event!</p>
        </div>

        <div v-else class="events-grid">
            <div
                v-for="event in filteredEvents"
                :key="event.id"
                class="event-card"
            >
                <div class="event-header">
                    <h3>{{ event.name }}</h3>
                    <p class="event-description">{{ event.description }}</p>
                    <div class="event-badges">
                        <span
                            v-if="event.visibility === 'private'"
                            class="badge private"
                        >
                            Private
                        </span>
                        <span
                            v-if="
                                authStore.user &&
                                event.organizers.includes(
                                    authStore.user.username,
                                )
                            "
                            class="badge organizer"
                        >
                            Organizer
                        </span>
                        <span
                            v-if="isParticipant(event)"
                            class="badge participant"
                        >
                            Participant
                        </span>
                    </div>
                </div>

                <div class="event-schedule">
                    <div class="schedule-compact">
                        <span class="schedule-text">
                            {{ formatDate(event.start_date) }}
                            <span
                                v-if="
                                    event.end_date &&
                                    event.end_date !== event.start_date
                                "
                            >
                                - {{ formatDate(event.end_date) }}
                            </span>
                        </span>
                    </div>
                    <div class="schedule-compact">
                        <span class="schedule-text">
                            {{ formatTime(event.start_time) }}
                            <span v-if="event.end_time"
                                >- {{ formatTime(event.end_time) }}</span
                            >
                        </span>
                    </div>
                </div>

                <div class="event-content">
                    <div class="event-section">
                        <h4>Locations</h4>
                        <div class="tags">
                            <span
                                v-for="location in event.locations"
                                :key="location"
                                class="tag"
                            >
                                {{ location }}
                            </span>
                        </div>
                    </div>

                    <div class="event-section">
                        <h4>Organizers</h4>
                        <div class="tags">
                            <span
                                v-for="organizer in event.organizers"
                                :key="organizer"
                                class="tag"
                            >
                                {{ organizer }}
                            </span>
                        </div>
                    </div>

                    <div
                        v-if="event.participants.length > 0"
                        class="event-section"
                    >
                        <h4>
                            Participants ({{ event.participants.length }})
                        </h4>
                        <div class="participants-summary">
                            <span
                                >Total Due: ${{
                                    totalDue(event).toFixed(2)
                                }}</span
                            >
                            <span
                                >Total Paid: ${{
                                    totalPaid(event).toFixed(2)
                                }}</span
                            >
                        </div>
                    </div>

                    <div v-if="event.notes.length > 0" class="event-section">
                        <h4>Notes</h4>
                        <ul class="notes-list">
                            <li
                                v-for="note in event.notes.slice(0, 2)"
                                :key="note"
                            >
                                {{ note }}
                            </li>
                            <li v-if="event.notes.length > 2">
                                ...and {{ event.notes.length - 2 }} more
                            </li>
                        </ul>
                    </div>
                </div>

                <div class="event-meta">
                    <span class="date"
                        >Created: {{ formatDate(event.created_at) }}</span
                    >
                    <span v-if="event.updated_at" class="updated">
                        Updated: {{ formatDate(event.updated_at) }}
                    </span>
                </div>

                <div class="event-actions">
                    <button
                        v-if="canJoinEvent(event)"
                        @click="joinEvent(event)"
                        class="join-btn"
                    >
                        Join Event
                    </button>
                    <button
                        v-if="canUnjoinEvent(event)"
                        @click="unjoinEvent(event)"
                        class="unjoin-btn"
                    >
                        Leave Event
                    </button>
                    <button
                        v-if="isOrganizer(event)"
                        class="join-btn disabled"
                        disabled
                        title="Organizers cannot leave their own event"
                    >
                        Organizer
                    </button>
                    <button @click="viewDetails(event)" class="details-btn">
                        View Details
                    </button>
                    <button
                        v-if="canManageEvent(event)"
                        @click="startEditEvent(event)"
                        class="edit-btn"
                    >
                        Edit
                    </button>
                    <button
                        v-if="canManageEvent(event)"
                        @click="deleteEvent(event.id)"
                        class="delete-btn"
                    >
                        Delete
                    </button>
                </div>
            </div>
        </div>

        <!-- Create Event Modal -->
        <div v-if="showCreateForm" class="modal-overlay" @click="closeModal">
            <div class="modal" @click.stop>
                <h2>Create New Event</h2>
                <EventForm
                    ref="createEventFormRef"
                    :use-textarea="true"
                    :current-username="authStore.user?.username"
                    submit-label="Create Event"
                    @submit="handleCreateEvent"
                    @cancel="closeModal"
                />
            </div>
        </div>

        <!-- Edit Event Modal -->
        <div v-if="showEditForm" class="modal-overlay" @click="closeEditModal">
            <div class="modal" @click.stop>
                <h2>Edit Event</h2>
                <form @submit.prevent="updateEvent">
                    <div class="form-group">
                        <label for="edit-name">Event Name</label>
                        <input
                            type="text"
                            id="edit-name"
                            v-model="editingEventData.name"
                            required
                            placeholder="Enter event name..."
                        />
                    </div>

                    <div class="form-group">
                        <label for="edit-description">Description</label>
                        <textarea
                            id="edit-description"
                            v-model="editingEventData.description"
                            rows="3"
                            required
                            placeholder="Describe the event..."
                        ></textarea>
                    </div>

                    <div class="form-group">
                        <label for="edit-visibility">Visibility</label>
                        <select id="edit-visibility" v-model="editingEventData.visibility">
                            <option value="public">Public - Anyone can find and join</option>
                            <option value="private">Private - Only invited users can join</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="edit-organizers"
                            >Organizers (one per line)</label
                        >
                        <textarea
                            id="edit-organizers"
                            v-model="editOrganizersText"
                            rows="3"
                            required
                            placeholder="Enter organizer names (one per line)"
                        ></textarea>
                    </div>

                    <div class="form-group">
                        <label for="edit-locations"
                            >Locations (one per line)</label
                        >
                        <textarea
                            id="edit-locations"
                            v-model="editLocationsText"
                            rows="3"
                            required
                            placeholder="Enter locations (one per line)"
                        ></textarea>
                    </div>

                    <div class="form-group">
                        <label for="edit-start_date">Start Date</label>
                        <input
                            type="date"
                            id="edit-start_date"
                            v-model="editingEventData.start_date"
                            required
                        />
                    </div>

                    <div class="form-group">
                        <label for="edit-end_date"
                            >End Date (optional for multi-day events)</label
                        >
                        <input
                            type="date"
                            id="edit-end_date"
                            v-model="editingEventData.end_date"
                            :min="editingEventData.start_date"
                        />
                    </div>

                    <div class="form-group">
                        <label for="edit-start_time">Start Time</label>
                        <input
                            type="time"
                            id="edit-start_time"
                            v-model="editingEventData.start_time"
                            required
                        />
                    </div>

                    <div class="form-group">
                        <label for="edit-end_time">End Time (optional)</label>
                        <input
                            type="time"
                            id="edit-end_time"
                            v-model="editingEventData.end_time"
                        />
                    </div>

                    <div class="form-group">
                        <label for="edit-notes"
                            >Notes (one per line, optional)</label
                        >
                        <textarea
                            id="edit-notes"
                            v-model="editNotesText"
                            rows="3"
                            placeholder="Enter any additional notes..."
                        ></textarea>
                    </div>

                    <div class="modal-actions">
                        <button
                            type="button"
                            @click="closeEditModal"
                            class="cancel-btn"
                        >
                            Cancel
                        </button>
                        <button type="submit" class="submit-btn">
                            Update Event
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Event Details Modal -->
        <div v-if="selectedEvent" class="modal-overlay" @click="closeDetails">
            <div class="modal details-modal" @click.stop>
                <div class="details-header">
                    <h2>{{ selectedEvent.name }}</h2>
                    <p class="event-description">
                        {{ selectedEvent.description }}
                    </p>
                    <button @click="closeDetails" class="close-btn">Close</button>
                </div>

                <div class="details-content">
                    <div class="detail-section">
                        <h3>Event Schedule</h3>
                        <div class="schedule-info">
                            <div class="schedule-row">
                                <span class="schedule-label">Start:</span>
                                <span class="schedule-value">
                                    {{ formatDate(selectedEvent.start_date) }}
                                    at
                                    {{ formatTime(selectedEvent.start_time) }}
                                </span>
                            </div>
                            <div
                                v-if="selectedEvent.end_date"
                                class="schedule-row"
                            >
                                <span class="schedule-label">End:</span>
                                <span class="schedule-value">
                                    {{ formatDate(selectedEvent.end_date) }}
                                    <span v-if="selectedEvent.end_time"
                                        >at
                                        {{
                                            formatTime(selectedEvent.end_time)
                                        }}</span
                                    >
                                </span>
                            </div>
                            <div
                                v-else-if="selectedEvent.end_time"
                                class="schedule-row"
                            >
                                <span class="schedule-label">End Time:</span>
                                <span class="schedule-value">{{
                                    formatTime(selectedEvent.end_time)
                                }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h3>Locations</h3>
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
                        <h3>Organizers</h3>
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
                        <h3>
                            Participants ({{
                                selectedEvent.participants.length
                            }})
                        </h3>
                        <div
                            v-if="selectedEvent.participants.length === 0"
                            class="empty-participants"
                        >
                            No participants yet
                        </div>
                        <div v-else class="participants-list">
                            <div
                                v-for="participant in selectedEvent.participants"
                                :key="participant.user_id"
                                class="participant-item"
                            >
                                <div class="participant-info">
                                    <strong>{{ participant.user_id }}</strong>
                                    <div
                                        v-if="participant.tags.length > 0"
                                        class="participant-tags"
                                    >
                                        <span
                                            v-for="tag in participant.tags"
                                            :key="tag"
                                            class="tag small"
                                        >
                                            {{ tag }}
                                        </span>
                                    </div>
                                </div>
                                <div class="payment-info">
                                    <span class="due"
                                        >Due: ${{
                                            participant.due_payment.toFixed(2)
                                        }}</span
                                    >
                                    <span class="paid"
                                        >Paid: ${{
                                            participant.paid_amount.toFixed(2)
                                        }}</span
                                    >
                                    <span
                                        :class="[
                                            'balance',
                                            {
                                                'paid-full':
                                                    participant.paid_amount >=
                                                    participant.due_payment,
                                                partial:
                                                    participant.paid_amount >
                                                        0 &&
                                                    participant.paid_amount <
                                                        participant.due_payment,
                                                unpaid:
                                                    participant.paid_amount ===
                                                    0,
                                            },
                                        ]"
                                    >
                                        Balance: ${{
                                            (
                                                participant.due_payment -
                                                participant.paid_amount
                                            ).toFixed(2)
                                        }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div
                        v-if="selectedEvent.notes.length > 0"
                        class="detail-section"
                    >
                        <h3>Notes</h3>
                        <ul class="notes-list">
                            <li v-for="note in selectedEvent.notes" :key="note">
                                {{ note }}
                            </li>
                        </ul>
                    </div>

                    <div
                        v-if="selectedEvent.images.length > 0"
                        class="detail-section"
                    >
                        <h3>Images</h3>
                        <div class="images-grid">
                            <div
                                v-for="image in selectedEvent.images"
                                :key="image"
                                class="image-item"
                            >
                                {{ image }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, reactive, nextTick } from "vue";
import { useEventStore } from "@/stores/events";
import { useAuthStore } from "@/stores/auth";
import EventForm from "@/components/EventForm.vue";
import { eventsAPI } from "@/utils/api";
import type { Event, EventCreate, Participant } from "@/types";

const eventStore = useEventStore();
const authStore = useAuthStore();

const createEventFormRef = ref<InstanceType<typeof EventForm> | null>(null);

const events = computed(() => eventStore.events);
const loading = computed(() => eventStore.loading);
const error = computed(() => eventStore.error);

const filterOrganizer = ref("");
const filterLocation = ref("");
const filterVisibility = ref("");
const showCreateForm = ref(false);
const showEditForm = ref(false);
const selectedEvent = ref<Event | null>(null);
const editingEvent = ref<Event | null>(null);
const editingEventData = reactive({
    name: "",
    description: "",
    organizers: [] as string[],
    locations: [] as string[],
    start_date: "",
    end_date: "",
    start_time: "",
    end_time: "",
    notes: [] as string[],
    visibility: "public" as "public" | "private",
});

const editOrganizersText = ref("");
const editLocationsText = ref("");
const editNotesText = ref("");

const filteredEvents = computed(() => {
    let filtered = events.value;

    if (filterOrganizer.value) {
        filtered = filtered.filter((event) =>
            event.organizers.some((org) =>
                org.toLowerCase().includes(filterOrganizer.value.toLowerCase()),
            ),
        );
    }

    if (filterLocation.value) {
        filtered = filtered.filter((event) =>
            event.locations.some((loc) =>
                loc.toLowerCase().includes(filterLocation.value.toLowerCase()),
            ),
        );
    }

    if (filterVisibility.value) {
        filtered = filtered.filter((event) =>
            event.visibility === filterVisibility.value
        );
    }

    return filtered;
});

onMounted(() => {
    eventStore.fetchEvents();
});

const handleCreateEvent = async (eventData: EventCreate) => {
    try {
        console.log("Sending event data:", eventData);
        await eventStore.createEvent(eventData);
        closeModal();
    } catch (error) {
        console.error("Failed to create event:", error);
    }
};

const deleteEvent = async (id: string) => {
    if (confirm("Are you sure you want to delete this event?")) {
        try {
            await eventStore.deleteEvent(id);
        } catch (error) {
            console.error("Failed to delete event:", error);
        }
    }
};

const openCreateModal = async () => {
    showCreateForm.value = true;
    await nextTick();
    if (authStore.user?.username) {
        createEventFormRef.value?.setInitialOrganizers(authStore.user.username);
    }
};

const viewDetails = (event: Event) => {
    selectedEvent.value = event;
};

const closeModal = () => {
    showCreateForm.value = false;
    createEventFormRef.value?.reset();
};

const startEditEvent = (event: Event) => {
    editingEvent.value = event;
    editingEventData.name = event.name;
    editingEventData.description = event.description;
    editingEventData.organizers = [...event.organizers];
    editingEventData.locations = [...event.locations];
    editingEventData.start_date = event.start_date;
    editingEventData.end_date = event.end_date || "";
    // Format time for HTML time input (HH:MM format from HH:MM:SS)
    editingEventData.start_time = event.start_time.substring(0, 5);
    editingEventData.end_time = event.end_time
        ? event.end_time.substring(0, 5)
        : "";
    editingEventData.notes = [...event.notes];
    editingEventData.visibility = (event.visibility as "public" | "private") || "public";

    editOrganizersText.value = event.organizers.join("\n");
    editLocationsText.value = event.locations.join("\n");
    editNotesText.value = event.notes.join("\n");

    showEditForm.value = true;
};

const updateEvent = async () => {
    if (!editingEvent.value) return;

    try {
        // Build update data, filtering out undefined values
        const updateData: any = {
            name: editingEventData.name,
            description: editingEventData.description,
            organizers: editingEventData.organizers,
            locations: editingEventData.locations,
            start_date: editingEventData.start_date,
            start_time: editingEventData.start_time + ":00", // Ensure HH:MM:SS format
            visibility: editingEventData.visibility,
        };

        // Only include optional fields if they have values
        if (editingEventData.end_date) {
            updateData.end_date = editingEventData.end_date;
        }
        if (editingEventData.end_time) {
            updateData.end_time = editingEventData.end_time + ":00";
        }
        if (editingEventData.notes.length > 0) {
            updateData.notes = editingEventData.notes;
        }

        console.log("Sending update data:", updateData);
        await eventStore.updateEvent(editingEvent.value.id, updateData);
        closeEditModal();
    } catch (error) {
        console.error("Failed to update event:", error);
    }
};

const closeEditModal = () => {
    showEditForm.value = false;
    editingEvent.value = null;
    editingEventData.name = "";
    editingEventData.description = "";
    editingEventData.organizers = [];
    editingEventData.locations = [];
    editingEventData.start_date = "";
    editingEventData.end_date = "";
    editingEventData.start_time = "";
    editingEventData.end_time = "";
    editingEventData.notes = [];
    editingEventData.visibility = "public";
    editOrganizersText.value = "";
    editLocationsText.value = "";
    editNotesText.value = "";
};

const closeDetails = () => {
    selectedEvent.value = null;
};

const clearFilters = () => {
    filterOrganizer.value = "";
    filterLocation.value = "";
    filterVisibility.value = "";
};

const canManageEvent = (event: Event): boolean => {
    if (!authStore.user) return false;
    return (
        authStore.isAdmin ||
        (authStore.isOrganizer &&
            event.organizers.includes(authStore.user.username))
    );
};

const isParticipant = (event: Event): boolean => {
    return event.participants.some(
        (p) => p.user_id === authStore.user?.username,
    );
};

const canJoinEvent = (event: Event): boolean => {
    if (!authStore.user) return false;
    if (isParticipant(event)) return false;
    if (isOrganizer(event)) return false;
    return event.visibility === "public";
};

const canUnjoinEvent = (event: Event): boolean => {
    if (!authStore.user) return false;
    if (isParticipant(event) && !isOrganizer(event)) return true;
    return false;
};

const isOrganizer = (event: Event): boolean => {
    if (!authStore.user) return false;
    return event.organizers.includes(authStore.user.username);
};

const joinEvent = async (event: Event) => {
    if (!authStore.user) return;
    
    const participant: Participant = {
        user_id: authStore.user.username,
        due_payment: 0,
        paid_amount: 0,
        tags: [],
    };
    
    try {
        await eventsAPI.addParticipant(event.id, participant);
        await eventStore.fetchEvents();
    } catch (error) {
        console.error("Failed to join event:", error);
    }
};

const unjoinEvent = async (event: Event) => {
    if (!authStore.user) return;
    
    if (!confirm("Are you sure you want to leave this event?")) return;
    
    try {
        await eventsAPI.removeParticipant(event.id, authStore.user.username);
        await eventStore.fetchEvents();
    } catch (error) {
        console.error("Failed to leave event:", error);
    }
};

const totalDue = (event: Event): number => {
    return event.participants.reduce((sum, p) => sum + p.due_payment, 0);
};

const totalPaid = (event: Event): number => {
    return event.participants.reduce((sum, p) => sum + p.paid_amount, 0);
};

const formatDate = (dateString: string) => {
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

// Watch edit form text areas and update arrays
watch(editOrganizersText, (newText) => {
    editingEventData.organizers = newText
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => line.length > 0);
});

watch(editLocationsText, (newText) => {
    editingEventData.locations = newText
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => line.length > 0);
});

watch(editNotesText, (newText) => {
    editingEventData.notes = newText
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => line.length > 0);
});
</script>

<style scoped>
.events-container {
    min-height: calc(100vh - 60px);
    max-width: 1280px;
    margin: 0 auto;
    padding: 3rem 1.5rem;
    background: linear-gradient(135deg, var(--primary-50) 0%, var(--white) 100%);
}

.events-header {
    margin-bottom: 2rem;
    animation: fadeInUp 0.6s ease-out;
}

.events-header h1 {
    color: var(--gray-900);
    margin: 0 0 1rem 0;
    font-size: 2rem;
    font-weight: 700;
}

.header-actions {
    display: flex;
    gap: 1rem;
    align-items: center;
    flex-wrap: wrap;
}

.filters {
    display: flex;
    gap: 0.75rem;
    flex: 1;
}

.filter-input {
    flex: 1;
    min-width: 200px;
    padding: 0.625rem 1rem;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 0.875rem;
    transition: all 0.2s ease;
    background-color: var(--white);
}

.filter-input:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
}

.filter-input::placeholder {
    color: var(--gray-400);
}

.create-btn {
    background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
    color: var(--white);
    border: none;
    padding: 0.625rem 1.5rem;
    border-radius: var(--radius-lg);
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
    white-space: nowrap;
    font-size: 0.875rem;
}

.create-btn:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.loading,
.error,
.empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--gray-600);
    background: var(--white);
    border-radius: var(--radius-xl);
    border: 1px solid var(--gray-200);
    box-shadow: var(--shadow-md);
    animation: fadeInUp 0.6s ease-out;
}

.error {
    color: #dc2626;
    background-color: #fef2f2;
    border-color: #fecaca;
}

.clear-filters {
    background: none;
    border: none;
    color: var(--primary-600);
    text-decoration: underline;
    cursor: pointer;
    font: inherit;
    font-weight: 500;
}

.clear-filters:hover {
    color: var(--primary-700);
}

.events-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 1.5rem;
}

.event-card {
    background: var(--white);
    border-radius: var(--radius-xl);
    padding: 1.5rem;
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
    border: 1px solid var(--gray-200);
    border-left: 4px solid var(--primary-500);
    animation: fadeInUp 0.6s ease-out;
}

.event-card:nth-child(2) { animation-delay: 0.1s; }
.event-card:nth-child(3) { animation-delay: 0.2s; }
.event-card:nth-child(4) { animation-delay: 0.3s; }
.event-card:nth-child(5) { animation-delay: 0.4s; }
.event-card:nth-child(6) { animation-delay: 0.5s; }

.event-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: var(--primary-200);
}

.event-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.event-schedule {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.schedule-compact {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    color: #555;
}

.schedule-icon {
    font-size: 1rem;
}

.schedule-text {
    font-weight: 500;
}

.event-header h3 {
    color: #333;
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    flex: 1;
}

.event-description {
    color: #666;
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.4;
}

.event-badges {
    display: flex;
    gap: 0.5rem;
    margin-left: 1rem;
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

.badge.private {
    background: #fff3e0;
    color: #e65100;
}

.event-section {
    margin-bottom: 1rem;
}

.event-section h4 {
    color: #555;
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.tag {
    background: #f8f9fa;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.8rem;
    color: #666;
}

.tag.small {
    font-size: 0.7rem;
}

.participants-summary {
    display: flex;
    gap: 1rem;
    font-size: 0.9rem;
    color: #666;
}

.notes-list {
    margin: 0;
    padding-left: 1.5rem;
    color: #666;
}

.notes-list li {
    margin-bottom: 0.25rem;
}

.event-meta {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-top: 1rem;
    font-size: 0.875rem;
    color: #888;
}

.event-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
}

.details-btn {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #667eea;
    background: white;
    color: #667eea;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.details-btn:hover {
    background: #667eea;
    color: white;
}

.join-btn {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #27ae60;
    background: white;
    color: #27ae60;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.join-btn:hover {
    background: #27ae60;
    color: white;
}

.join-btn.disabled {
    border-color: #ccc;
    color: #999;
    cursor: not-allowed;
}

.join-btn.disabled:hover {
    background: white;
    color: #999;
}

.unjoin-btn {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #e74c3c;
    background: white;
    color: #e74c3c;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.unjoin-btn:hover {
    background: #e74c3c;
    color: white;
}

.edit-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #f39c12;
    background: white;
    color: #f39c12;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.edit-btn:hover {
    background: #f39c12;
    color: white;
}

.delete-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #e74c3c;
    background: white;
    color: #e74c3c;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.delete-btn:hover {
    background: #e74c3c;
    color: white;
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
    padding: 2rem;
    border-radius: 12px;
    max-width: 1000px;
    width: 98%;
    max-height: 90vh;
    overflow-y: auto;
}

.details-modal {
    max-width: 800px;
}

.details-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.details-header h2 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.details-header .event-description {
    color: #666;
    margin: 0;
    font-size: 0.95rem;
    line-height: 1.4;
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

.empty-participants {
    color: #888;
    font-style: italic;
}

.participants-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.participant-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.participant-info {
    flex: 1;
}

.participant-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    margin-top: 0.5rem;
}

.payment-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.9rem;
    text-align: right;
}

.due {
    color: #e74c3c;
}

.paid {
    color: #27ae60;
}

.balance {
    font-weight: 500;
}

.balance.paid-full {
    color: #27ae60;
}

.balance.partial {
    color: #f39c12;
}

.balance.unpaid {
    color: #e74c3c;
}

.images-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
}

.image-item {
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 6px;
    text-align: center;
    font-size: 0.9rem;
    color: #666;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #333;
    font-weight: 500;
}

.form-group textarea,
.form-group input,
.form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.form-group textarea {
    resize: vertical;
}

.form-group textarea:focus,
.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: #667eea;
}

.modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
}

.cancel-btn {
    padding: 0.75rem 1.5rem;
    border: 1px solid #ddd;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.cancel-btn:hover {
    background: #f8f9fa;
}

.submit-btn {
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
    transform: translateY(-2px);
}

.submit-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.dates-input {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.date-input-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.date-input-group input {
    flex: 1;
    padding: 0.75rem;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.date-input-group input:focus {
    outline: none;
    border-color: #667eea;
}

.remove-date-btn {
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 50%;
    width: 2rem;
    height: 2rem;
    cursor: pointer;
    font-size: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.3s ease;
}

.remove-date-btn:hover {
    background: #c0392b;
}

.add-date-btn {
    background: #27ae60;
    color: white;
    border: none;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.3s ease;
    align-self: flex-start;
}

.add-date-btn:hover {
    background: #229954;
}

.dates-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.schedule-info {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.schedule-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.schedule-label {
    font-weight: 600;
    color: #333;
    min-width: 80px;
}

.schedule-value {
    color: #555;
    font-weight: 500;
}

@media (max-width: 768px) {
    .events-container {
        padding: 1rem;
    }

    .header-actions {
        flex-direction: column;
        align-items: stretch;
    }

    .filters {
        flex-direction: column;
    }

    .filter-input {
        min-width: auto;
    }

    .events-grid {
        grid-template-columns: 1fr;
    }

    .modal {
        padding: 1.5rem;
    }

    .participant-item {
        flex-direction: column;
        gap: 0.5rem;
    }

    .payment-info {
        text-align: left;
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
