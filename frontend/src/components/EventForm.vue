<template>
    <form @submit.prevent="handleSubmit">
        <div class="form-group">
            <label for="event-name">Event Name</label>
            <input
                id="event-name"
                v-model="localEvent.name"
                type="text"
                required
                placeholder="Enter event name..."
            />
        </div>

        <div class="form-group">
            <label for="event-description">Description</label>
            <textarea
                id="event-description"
                v-model="localEvent.description"
                rows="3"
                required
                placeholder="Describe the event..."
            ></textarea>
        </div>

        <div class="form-group">
            <label for="event-visibility">Visibility</label>
            <select id="event-visibility" v-model="localEvent.visibility">
                <option value="public">Public - Anyone can find and join</option>
                <option value="private">Private - Only invited users can join</option>
            </select>
        </div>

        <div class="form-group">
            <label :for="organizersId">{{ organizersLabel }}</label>
            <textarea
                v-if="useTextarea"
                :id="organizersId"
                v-model="localOrganizersText"
                rows="3"
                required
                :placeholder="organizersPlaceholder"
            ></textarea>
            <input
                v-else
                :id="organizersId"
                v-model="localOrganizersText"
                type="text"
                required
                :placeholder="organizersPlaceholder"
            />
        </div>

        <div class="form-group">
            <label :for="locationsId">{{ locationsLabel }}</label>
            <textarea
                v-if="useTextarea"
                :id="locationsId"
                v-model="localLocationsText"
                rows="3"
                required
                :placeholder="locationsPlaceholder"
            ></textarea>
            <input
                v-else
                :id="locationsId"
                v-model="localLocationsText"
                type="text"
                required
                :placeholder="locationsPlaceholder"
            />
        </div>

        <div class="form-group">
            <label for="event-start-date">Start Date</label>
            <input
                id="event-start-date"
                v-model="localEvent.start_date"
                type="date"
                required
                :min="minDate"
            />
        </div>

        <div class="form-group">
            <label for="event-end-date">End Date (optional for multi-day events)</label>
            <input
                id="event-end-date"
                v-model="localEvent.end_date"
                type="date"
                :min="localEvent.start_date"
            />
        </div>

        <div class="form-group">
            <label for="event-start-time">Start Time</label>
            <input
                id="event-start-time"
                v-model="localEvent.start_time"
                type="time"
                required
            />
        </div>

        <div class="form-group">
            <label for="event-end-time">End Time (optional)</label>
            <input
                id="event-end-time"
                v-model="localEvent.end_time"
                type="time"
            />
        </div>

        <div class="form-group">
            <label for="event-notes">{{ notesLabel }}</label>
            <textarea
                v-if="useTextarea"
                id="event-notes"
                v-model="localNotesText"
                rows="3"
                :placeholder="notesPlaceholder"
            ></textarea>
            <input
                v-else
                id="event-notes"
                v-model="localNotesText"
                type="text"
                :placeholder="notesPlaceholder"
            />
        </div>

        <div class="modal-actions">
            <button type="button" @click="handleCancel" class="cancel-btn">
                Cancel
            </button>
            <button type="submit" class="submit-btn" :disabled="!isFormValid">
                {{ submitLabel }}
            </button>
        </div>
    </form>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from "vue";
import type { EventCreate } from "@/types";

const props = withDefaults(defineProps<{
    event?: EventCreate;
    useTextarea?: boolean;
    inputSeparator?: string;
    submitLabel?: string;
    organizersLabel?: string;
    locationsLabel?: string;
    notesLabel?: string;
    organizersPlaceholder?: string;
    locationsPlaceholder?: string;
    notesPlaceholder?: string;
}>(), {
    useTextarea: true,
    inputSeparator: "\n",
    submitLabel: "Create Event",
    organizersLabel: "Organizers (one per line)",
    locationsLabel: "Locations (one per line)",
    notesLabel: "Notes (one per line, optional)",
    organizersPlaceholder: "Enter organizer names (one per line)",
    locationsPlaceholder: "Enter locations (one per line)",
    notesPlaceholder: "Enter any additional notes..."
});

const emit = defineEmits<{
    submit: [event: EventCreate];
    cancel: [];
}>();

const localEvent = reactive<EventCreate>({
    name: props.event?.name || "",
    description: props.event?.description || "",
    organizers: props.event?.organizers || [],
    locations: props.event?.locations || [],
    start_date: props.event?.start_date || "",
    end_date: props.event?.end_date || "",
    start_time: props.event?.start_time || "",
    end_time: props.event?.end_time || "",
    notes: props.event?.notes || [],
    visibility: props.event?.visibility || "public",
});

const localOrganizersText = ref(props.event?.organizers?.join("\n") || "");
const localLocationsText = ref(props.event?.locations?.join("\n") || "");
const localNotesText = ref(props.event?.notes?.join("\n") || "");

const minDate = computed(() => {
    return new Date().toISOString().split("T")[0];
});

const isFormValid = computed(() => {
    return (
        localEvent.name.trim() &&
        localEvent.description.trim() &&
        localEvent.organizers.length > 0 &&
        localEvent.locations.length > 0 &&
        localEvent.start_date &&
        localEvent.start_time
    );
});

const organizersId = computed(() => props.useTextarea ? "event-organizers" : "event-organizers-input");
const locationsId = computed(() => props.useTextarea ? "event-locations" : "event-locations-input");

watch(localOrganizersText, (newText) => {
    localEvent.organizers = newText
        .split(props.inputSeparator)
        .map((line) => line.trim())
        .filter((line) => line.length > 0);
});

watch(localLocationsText, (newText) => {
    localEvent.locations = newText
        .split(props.inputSeparator)
        .map((line) => line.trim())
        .filter((line) => line.length > 0);
});

watch(localNotesText, (newText) => {
    localEvent.notes = newText
        .split(props.inputSeparator)
        .map((line) => line.trim())
        .filter((line) => line.length > 0);
});

const handleSubmit = () => {
    const eventData: EventCreate = {
        ...localEvent,
        start_time: localEvent.start_time + ":00",
        ...(localEvent.end_time && { end_time: localEvent.end_time + ":00" }),
    };
    emit("submit", eventData);
};

const handleCancel = () => {
    emit("cancel");
};

defineExpose({
    reset: () => {
        localEvent.name = "";
        localEvent.description = "";
        localEvent.organizers = [];
        localEvent.locations = [];
        localEvent.start_date = "";
        localEvent.end_date = "";
        localEvent.start_time = "";
        localEvent.end_time = "";
        localEvent.notes = [];
        localEvent.visibility = "public";
        localOrganizersText.value = "";
        localLocationsText.value = "";
        localNotesText.value = "";
    },
    setInitialOrganizers: (text: string) => {
        localOrganizersText.value = text;
    }
});
</script>

<style scoped>
form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
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
    box-sizing: border-box;
}

.form-group textarea {
    resize: vertical;
    min-height: 80px;
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
    margin-top: 1.5rem;
}

.cancel-btn {
    padding: 0.75rem 1.5rem;
    border: 1px solid #ddd;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    font-size: 1rem;
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
    transition: transform 0.3s ease, opacity 0.3s ease;
    font-size: 1rem;
}

.submit-btn:hover:not(:disabled) {
    transform: translateY(-2px);
}

.submit-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}
</style>
