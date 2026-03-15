<template>
    <div class="admin-container">
        <h1>Admin Panel</h1>
        <div class="admin-tabs">
            <button
                @click="activeTab = 'users'"
                :class="{ active: activeTab === 'users' }"
                class="tab-btn"
            >
                Users
            </button>
            <button
                @click="activeTab = 'events'"
                :class="{ active: activeTab === 'events' }"
                class="tab-btn"
            >
                Events
            </button>
        </div>

        <!-- Users Tab -->
        <div v-if="activeTab === 'users'" class="tab-content">
            <div class="tab-header">
                <h2>All Users</h2>
                <button @click="showCreateUserForm = true" class="create-btn">
                    + Create User
                </button>
            </div>
            <div v-if="usersLoading" class="loading">Loading users...</div>
            <div v-else-if="usersError" class="error">{{ usersError }}</div>
            <div v-else class="users-table">
                <table>
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="user in users" :key="user.id">
                            <td>
                                <div v-if="editingUser?.id === user.id" class="editable-field">
                                    <input 
                                        v-model="editingUserData.username" 
                                        class="edit-input"
                                        @blur="cancelEditUser"
                                        @keyup.enter="saveUser"
                                        @keyup.escape="cancelEditUser"
                                        ref="usernameInput"
                                    />
                                </div>
                                <span v-else @click="startEditUser(user)" class="editable-text">
                                    {{ user.username }}
                                </span>
                            </td>
                            <td>
                                <div v-if="editingUser?.id === user.id" class="editable-field">
                                    <input 
                                        v-model="editingUserData.email" 
                                        type="email"
                                        class="edit-input"
                                        @blur="cancelEditUser"
                                        @keyup.enter="saveUser"
                                        @keyup.escape="cancelEditUser"
                                    />
                                </div>
                                <span v-else @click="startEditUser(user)" class="editable-text">
                                    {{ user.email }}
                                </span>
                            </td>
                            <td>
                                <div v-if="editingUser?.id === user.id" class="editable-field">
                                    <select v-model="editingUserData.role" class="edit-select">
                                        <option value="user">User</option>
                                        <option value="organizer">Organizer</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </div>
                                <span v-else @click="startEditUser(user)" :class="['role-badge', user.role]">
                                    {{ user.role }}
                                </span>
                            </td>
                            <td>{{ formatDate(user.created_at) }}</td>
                            <td>
                                <div class="action-buttons">
                                    <button 
                                        v-if="editingUser?.id === user.id"
                                        @click="saveUser" 
                                        class="save-btn"
                                        title="Save"
                                    >
                                        ✓
                                    </button>
                                    <button 
                                        v-if="editingUser?.id === user.id"
                                        @click="cancelEditUser" 
                                        class="cancel-btn"
                                        title="Cancel"
                                    >
                                        ✗
                                    </button>
                                    <button 
                                        v-else
                                        @click="deleteUser(user.id)" 
                                        class="delete-btn"
                                        title="Delete User"
                                    >
                                        🗑
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Events Tab -->
        <div v-if="activeTab === 'events'" class="tab-content">
            <div class="tab-header">
                <h2>All Events</h2>
                <button @click="showCreateEventForm = true" class="create-btn">
                    + Create Event
                </button>
            </div>
            <div v-if="eventsLoading" class="loading">Loading events...</div>
            <div v-else-if="eventsError" class="error">{{ eventsError }}</div>
            <div v-else class="events-table">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Description</th>
                            <th>Organizers</th>
                            <th>Locations</th>
                            <th>Date</th>
                            <th>Participants</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="event in allEvents" :key="event.id">
                            <td>
                                <div v-if="editingEvent?.id === event.id" class="editable-field">
                                    <input 
                                        v-model="editingEventData.name" 
                                        class="edit-input"
                                        @blur="cancelEditEvent"
                                        @keyup.enter="saveEvent"
                                        @keyup.escape="cancelEditEvent"
                                    />
                                </div>
                                <span v-else @click="startEditEvent(event)" class="editable-text">
                                    {{ event.name }}
                                </span>
                            </td>
                            <td>
                                <div v-if="editingEvent?.id === event.id" class="editable-field">
                                    <textarea 
                                        v-model="editingEventData.description" 
                                        class="edit-textarea"
                                        rows="2"
                                        @blur="cancelEditEvent"
                                        @keyup.enter="saveEvent"
                                        @keyup.escape="cancelEditEvent"
                                    />
                                </div>
                                <span v-else @click="startEditEvent(event)" class="editable-text description">
                                    {{ event.description }}
                                </span>
                            </td>
                            <td>
                                <div v-if="editingEvent?.id === event.id" class="editable-field">
                                    <input 
                                        v-model="editOrganizersText" 
                                        class="edit-input"
                                        placeholder="comma separated"
                                        @blur="cancelEditEvent"
                                        @keyup.enter="saveEvent"
                                        @keyup.escape="cancelEditEvent"
                                    />
                                </div>
                                <span v-else @click="startEditEvent(event)" class="editable-text">
                                    {{ event.organizers.join(', ') }}
                                </span>
                            </td>
                            <td>
                                <div v-if="editingEvent?.id === event.id" class="editable-field">
                                    <input 
                                        v-model="editLocationsText" 
                                        class="edit-input"
                                        placeholder="comma separated"
                                        @blur="cancelEditEvent"
                                        @keyup.enter="saveEvent"
                                        @keyup.escape="cancelEditEvent"
                                    />
                                </div>
                                <span v-else @click="startEditEvent(event)" class="editable-text">
                                    {{ event.locations.join(', ') }}
                                </span>
                            </td>
                            <td>
                                <div v-if="editingEvent?.id === event.id" class="editable-field">
                                    <input 
                                        v-model="editStartDate" 
                                        type="date"
                                        class="edit-input"
                                        @blur="cancelEditEvent"
                                        @keyup.enter="saveEvent"
                                        @keyup.escape="cancelEditEvent"
                                    />
                                </div>
                                <span v-else @click="startEditEvent(event)" class="editable-text">
                                    {{ formatDate(event.start_date) }}
                                </span>
                            </td>
                            <td>{{ event.participants.length }}</td>
                            <td>
                                <div class="action-buttons">
                                    <button 
                                        v-if="editingEvent?.id === event.id"
                                        @click="saveEvent" 
                                        class="save-btn"
                                        title="Save"
                                    >
                                        ✓
                                    </button>
                                    <button 
                                        v-if="editingEvent?.id === event.id"
                                        @click="cancelEditEvent" 
                                        class="cancel-btn"
                                        title="Cancel"
                                    >
                                        ✗
                                    </button>
                                    <button 
                                        v-else
                                        @click="deleteEvent(event.id)" 
                                        class="delete-btn"
                                        title="Delete Event"
                                    >
                                        🗑
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Create User Modal -->
        <div v-if="showCreateUserForm" class="modal-overlay" @click="closeCreateUserModal">
            <div class="modal" @click.stop>
                <h2>Create User</h2>
                <form @submit.prevent="createUser">
                    <div class="form-group">
                        <label for="create-username">Username</label>
                        <input
                            id="create-username"
                            v-model="newUser.username"
                            type="text"
                            required
                            placeholder="Enter username"
                        />
                    </div>
                    <div class="form-group">
                        <label for="create-email">Email</label>
                        <input
                            id="create-email"
                            v-model="newUser.email"
                            type="email"
                            required
                            placeholder="Enter email"
                        />
                    </div>
                    <div class="form-group">
                        <label for="create-password">Password</label>
                        <input
                            id="create-password"
                            v-model="newUser.password"
                            type="password"
                            required
                            placeholder="Enter password"
                        />
                    </div>
                    <div class="form-group">
                        <label for="create-role">Role</label>
                        <select id="create-role" v-model="newUser.role" required>
                            <option value="user">User</option>
                            <option value="organizer">Organizer</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>
                    <div class="modal-actions">
                        <button type="button" @click="closeCreateUserModal" class="cancel-btn">
                            Cancel
                        </button>
                        <button type="submit" class="submit-btn">Create User</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Create Event Modal -->
        <div v-if="showCreateEventForm" class="modal-overlay" @click="closeCreateEventModal">
            <div class="modal" @click.stop>
                <h2>Create Event</h2>
                <form @submit.prevent="createEvent">
                    <div class="form-group">
                        <label for="create-event-name">Event Name</label>
                        <input
                            id="create-event-name"
                            v-model="newEvent.name"
                            type="text"
                            required
                            placeholder="Enter event name"
                        />
                    </div>
                    <div class="form-group">
                        <label for="create-description">Description</label>
                        <textarea
                            id="create-description"
                            v-model="newEvent.description"
                            rows="3"
                            required
                            placeholder="Describe the event..."
                        ></textarea>
                    </div>
                    <div class="form-group">
                        <label for="create-visibility">Visibility</label>
                        <select id="create-visibility" v-model="newEvent.visibility">
                            <option value="public">Public - Anyone can find and join</option>
                            <option value="private">Private - Only invited users can join</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="create-organizers">Organizers (comma separated)</label>
                        <input
                            id="create-organizers"
                            v-model="createOrganizersText"
                            type="text"
                            required
                            placeholder="Enter organizer names"
                        />
                    </div>
                    <div class="form-group">
                        <label for="create-locations">Locations (comma separated)</label>
                        <input
                            id="create-locations"
                            v-model="createLocationsText"
                            type="text"
                            required
                            placeholder="Enter locations"
                        />
                    </div>
                    <div class="form-group">
                        <label for="create-start-date">Start Date</label>
                        <input
                            id="create-start-date"
                            v-model="newEvent.start_date"
                            type="date"
                            required
                        />
                    </div>
                    <div class="form-group">
                        <label for="create-end-date">End Date (optional)</label>
                        <input
                            id="create-end-date"
                            v-model="newEvent.end_date"
                            type="date"
                        />
                    </div>
                    <div class="form-group">
                        <label for="create-start-time">Start Time</label>
                        <input
                            id="create-start-time"
                            v-model="newEvent.start_time"
                            type="time"
                            required
                        />
                    </div>
                    <div class="form-group">
                        <label for="create-end-time">End Time (optional)</label>
                        <input
                            id="create-end-time"
                            v-model="newEvent.end_time"
                            type="time"
                        />
                    </div>
                    <div class="modal-actions">
                        <button type="button" @click="closeCreateEventModal" class="cancel-btn">
                            Cancel
                        </button>
                        <button type="submit" class="submit-btn">Create Event</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive, nextTick } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useEventStore } from "@/stores/events";
import { authAPI, eventsAPI } from "@/utils/api";
import type { User, Event, EventCreate, UserCreate } from "@/types";

const authStore = useAuthStore();
const eventStore = useEventStore();

const activeTab = ref("users");
const users = ref<User[]>([]);
const usersLoading = ref(false);
const usersError = ref("");

const allEvents = computed(() => eventStore.events);
const eventsLoading = computed(() => eventStore.loading);
const eventsError = computed(() => eventStore.error);

// User editing
const editingUser = ref<User | null>(null);
const editingUserData = reactive({
    username: "",
    email: "",
    role: "",
});

// Event editing
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
});

const editOrganizersText = ref("");
const editLocationsText = ref("");
const editStartDate = ref("");

// Create user modal
const showCreateUserForm = ref(false);
const newUser = reactive<UserCreate>({
    username: "",
    email: "",
    password: "",
    role: "user",
});

// Create event modal
const showCreateEventForm = ref(false);
const newEvent = reactive<EventCreate>({
    name: "",
    organizers: [],
    locations: [],
    description: "",
    start_date: "",
    end_date: "",
    start_time: "",
    end_time: "",
    images: [],
    notes: [],
    visibility: "public",
    participants: [],
});

const createOrganizersText = ref("");
const createLocationsText = ref("");

onMounted(async () => {
    await Promise.all([fetchUsers(), fetchAllEvents()]);
});

const fetchUsers = async () => {
    usersLoading.value = true;
    usersError.value = "";
    try {
        users.value = await authAPI.getUsers();
    } catch (err: any) {
        usersError.value =
            err.response?.data?.detail || "Failed to fetch users";
    } finally {
        usersLoading.value = false;
    }
};

const fetchAllEvents = async () => {
    try {
        await eventStore.fetchEvents();
    } catch (err) {
        console.error("Failed to fetch events:", err);
    }
};

const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
};

// User functions
const startEditUser = (user: User) => {
    editingUser.value = user;
    editingUserData.username = user.username;
    editingUserData.email = user.email;
    editingUserData.role = user.role;
    nextTick(() => {
        const input = document.querySelector('input[ref="usernameInput"]') as HTMLInputElement;
        if (input) input.focus();
    });
};

const saveUser = async () => {
    if (!editingUser.value) return;
    
    try {
        await authAPI.updateUser(editingUser.value.id, editingUserData);
        await fetchUsers();
        cancelEditUser();
    } catch (error) {
        console.error("Failed to update user:", error);
    }
};

const cancelEditUser = () => {
    editingUser.value = null;
    editingUserData.username = "";
    editingUserData.email = "";
    editingUserData.role = "";
};

const deleteUser = async (userId: string) => {
    if (confirm("Are you sure you want to delete this user?")) {
        try {
            await authAPI.deleteUser(userId);
            await fetchUsers();
        } catch (error) {
            console.error("Failed to delete user:", error);
        }
    }
};

const createUser = async () => {
    try {
        await authAPI.register(newUser);
        await fetchUsers();
        closeCreateUserModal();
    } catch (error) {
        console.error("Failed to create user:", error);
    }
};

const closeCreateUserModal = () => {
    showCreateUserForm.value = false;
    newUser.username = "";
    newUser.email = "";
    newUser.password = "";
    newUser.role = "user";
};

// Event functions
const startEditEvent = (event: Event) => {
    editingEvent.value = event;
    editingEventData.name = event.name;
    editingEventData.description = event.description;
    editingEventData.organizers = [...event.organizers];
    editingEventData.locations = [...event.locations];
    editingEventData.start_date = event.start_date;
    editingEventData.end_date = event.end_date || "";
    editingEventData.start_time = event.start_time;
    editingEventData.end_time = event.end_time || "";

    editOrganizersText.value = event.organizers.join(", ");
    editLocationsText.value = event.locations.join(", ");
    editStartDate.value = event.start_date;
};

const saveEvent = async () => {
    if (!editingEvent.value) return;

    try {
        const updateData = {
            name: editingEventData.name,
            description: editingEventData.description,
            organizers: editOrganizersText.value.split(",").map(s => s.trim()).filter(s => s),
            locations: editLocationsText.value.split(",").map(s => s.trim()).filter(s => s),
            start_date: editingEventData.start_date,
            end_date: editingEventData.end_date || undefined,
            start_time: editingEventData.start_time,
            end_time: editingEventData.end_time || undefined,
        };
        
        await eventsAPI.updateEvent(editingEvent.value.id, updateData);
        await fetchAllEvents();
        cancelEditEvent();
    } catch (error) {
        console.error("Failed to update event:", error);
    }
};

const cancelEditEvent = () => {
    editingEvent.value = null;
    editingEventData.name = "";
    editingEventData.description = "";
    editingEventData.organizers = [];
    editingEventData.locations = [];
    editingEventData.start_date = "";
    editingEventData.end_date = "";
    editingEventData.start_time = "";
    editingEventData.end_time = "";
    editOrganizersText.value = "";
    editLocationsText.value = "";
    editStartDate.value = "";
};

const deleteEvent = async (eventId: string) => {
    if (confirm("Are you sure you want to delete this event?")) {
        try {
            await eventsAPI.deleteEvent(eventId);
            await fetchAllEvents();
        } catch (error) {
            console.error("Failed to delete event:", error);
        }
    }
};

const createEvent = async () => {
    try {
        const eventData = {
            ...newEvent,
            organizers: createOrganizersText.value.split(",").map(s => s.trim()).filter(s => s),
            locations: createLocationsText.value.split(",").map(s => s.trim()).filter(s => s),
        };
        
        await eventStore.createEvent(eventData);
        await fetchAllEvents();
        closeCreateEventModal();
    } catch (error) {
        console.error("Failed to create event:", error);
    }
};

const closeCreateEventModal = () => {
    showCreateEventForm.value = false;
    newEvent.name = "";
    newEvent.description = "";
    newEvent.organizers = [];
    newEvent.locations = [];
    newEvent.start_date = "";
    newEvent.end_date = "";
    newEvent.start_time = "";
    newEvent.end_time = "";
    createOrganizersText.value = "";
    createLocationsText.value = "";
};
</script>

<style scoped>
.admin-container {
    max-width: 1600px;
    margin: 0 auto;
    padding: 2rem;
}

.admin-container h1 {
    color: #333;
    margin-bottom: 2rem;
}

.admin-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    border-bottom: 2px solid #e1e5e9;
}

.tab-btn {
    padding: 1rem 1.5rem;
    border: none;
    background: transparent;
    color: #666;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    transition: all 0.3s ease;
}

.tab-btn.active {
    color: #667eea;
    border-bottom-color: #667eea;
}

.tab-btn:hover {
    color: #667eea;
}

.tab-content {
    animation: fadeIn 0.3s ease;
}

.tab-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.tab-header h2 {
    color: #333;
    margin: 0;
}

.create-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: transform 0.3s ease;
}

.create-btn:hover {
    transform: translateY(-2px);
}

.loading,
.error {
    text-align: center;
    padding: 2rem;
    color: #666;
}

.error {
    color: #e74c3c;
    background-color: #fdf2f2;
    border-radius: 8px;
    border: 1px solid #f5c6cb;
}

.users-table,
.events-table {
    overflow-x: auto;
}

.users-table table,
.events-table table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.users-table th,
.users-table td,
.events-table th,
.events-table td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #e1e5e9;
}

.users-table th,
.events-table th {
    background: #f8f9fa;
    font-weight: 600;
    color: #333;
}

.users-table tr:hover,
.events-table tr:hover {
    background: #f8f9fa;
}

.editable-field {
    min-width: 120px;
}

.editable-text {
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    display: block;
    min-height: 1.5rem;
    transition: background-color 0.2s ease;
}

.editable-text:hover {
    background-color: #f0f8ff;
}

.editable-text.description {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.edit-input,
.edit-textarea,
.edit-select {
    width: 100%;
    padding: 0.5rem;
    border: 2px solid #667eea;
    border-radius: 4px;
    font-size: 0.9rem;
    background: white;
}

.edit-textarea {
    resize: vertical;
    min-height: 60px;
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
}

.save-btn {
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    width: 2rem;
    height: 2rem;
    cursor: pointer;
    font-size: 0.8rem;
    transition: background-color 0.3s ease;
}

.save-btn:hover {
    background: #229954;
}

.cancel-btn {
    background: #f39c12;
    color: white;
    border: none;
    border-radius: 4px;
    width: 2rem;
    height: 2rem;
    cursor: pointer;
    font-size: 0.8rem;
    transition: background-color 0.3s ease;
}

.cancel-btn:hover {
    background: #e67e22;
}

.delete-btn {
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 4px;
    width: 2rem;
    height: 2rem;
    cursor: pointer;
    font-size: 0.8rem;
    transition: background-color 0.3s ease;
}

.delete-btn:hover {
    background: #c0392b;
}

.role-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: capitalize;
}

.role-badge.user {
    background: #e3f2fd;
    color: #1976d2;
}

.role-badge.admin {
    background: #f3e5f5;
    color: #7b1fa2;
}

.role-badge.organizer {
    background: #e8f5e8;
    color: #27ae60;
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
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal h2 {
    margin-top: 0;
    color: #333;
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

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
    box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus,
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

.submit-btn:hover {
    transform: translateY(-2px);
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 768px) {
    .admin-container {
        padding: 1rem;
    }

    .admin-tabs {
        overflow-x: auto;
    }

    .tab-btn {
        white-space: nowrap;
    }

    .users-table,
    .events-table {
        font-size: 0.875rem;
    }

    .tab-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }

    .modal {
        padding: 1rem;
    }
}
</style>