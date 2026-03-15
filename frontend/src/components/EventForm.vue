<template>
    <form @submit.prevent="handleSubmit">
        <div class="form-columns">
            <div class="form-column left">
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
                        rows="2"
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
                    <template v-if="useLocationTags">
                        <div class="location-input-row">
                            <input
                                id="event-locations-input"
                                v-model="locationInput"
                                type="text"
                                :placeholder="locationsPlaceholder"
                                @keydown.enter.prevent="addLocation"
                            />
                            <button type="button" class="btn-secondary" @click="addLocation">
                                Add
                            </button>
                        </div>
                        <div v-if="localEvent.locations.length > 0" class="locations-list">
                            <span
                                v-for="(loc, index) in localEvent.locations"
                                :key="index"
                                class="location-tag"
                            >
                                {{ loc }}
                                <button type="button" class="remove-btn" @click="removeLocation(index)">×</button>
                            </span>
                        </div>
                    </template>
                    <template v-else>
                        <textarea
                            v-if="useTextarea"
                            :id="locationsId"
                            v-model="localLocationsText"
                            rows="2"
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
                    </template>
                </div>
            </div>

            <div class="form-column right">
                <div class="form-row-group">
                    <div class="form-group half">
                        <label for="event-start-date">Start Date</label>
                        <input
                            id="event-start-date"
                            v-model="localEvent.start_date"
                            type="date"
                            required
                            :min="minDate"
                        />
                    </div>

                    <div class="form-group half">
                        <label for="event-start-time">Start Time</label>
                        <input
                            id="event-start-time"
                            v-model="localEvent.start_time"
                            type="time"
                            required
                        />
                    </div>
                </div>

                <div class="form-row-group">
                    <div class="form-group half">
                        <label for="event-end-date">End Date (optional)</label>
                        <input
                            id="event-end-date"
                            v-model="localEvent.end_date"
                            type="date"
                            :min="localEvent.start_date"
                        />
                    </div>

                    <div class="form-group half">
                        <label for="event-end-time">End Time (optional)</label>
                        <input
                            id="event-end-time"
                            v-model="localEvent.end_time"
                            type="time"
                        />
                    </div>
                </div>

                <div class="form-group">
                    <label for="event-notes">{{ notesLabel }}</label>
                    <textarea
                        v-if="useTextarea"
                        id="event-notes"
                        v-model="localNotesText"
                        rows="4"
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
            </div>
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
    useLocationTags?: boolean;
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
    useLocationTags: false,
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
const locationInput = ref("");

const addLocation = () => {
    if (locationInput.value.trim()) {
        localEvent.locations.push(locationInput.value.trim());
        locationInput.value = "";
    }
};

const removeLocation = (index: number) => {
    localEvent.locations.splice(index, 1);
};

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

.form-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.form-column {
    display: flex;
    flex-direction: column;
}

.form-column.left {
    padding-right: 1rem;
}

.form-column.right {
    padding-left: 1rem;
    border-left: 1px solid #e1e5e9;
}

.form-row-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
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

.form-group.half {
    margin-bottom: 0.75rem;
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
    min-height: 60px;
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
    padding-top: 1rem;
    border-top: 1px solid #e1e5e9;
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

.location-input-row {
    display: flex;
    gap: 0.5rem;
}

.location-input-row input {
    flex: 1;
}

.btn-secondary {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    white-space: nowrap;
    transition: background-color 0.2s ease;
}

.btn-secondary:hover {
    background: #f0f0f0;
}

.locations-list {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}

.location-tag {
    background: #e3f2fd;
    color: #1976d2;
    padding: 0.3rem 0.6rem;
    border-radius: 12px;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}

.remove-btn {
    background: none;
    border: none;
    color: #1976d2;
    cursor: pointer;
    padding: 0;
    font-size: 1rem;
    line-height: 1;
}

.remove-btn:hover {
    color: #d32f2f;
}

.submit-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}
</style>
