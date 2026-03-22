<template>
  <div class="organizer-view">
    <div class="organizer-header">
      <h1>{{ authStore.isAdmin ? 'Event Management' : 'My Events' }}</h1>
      <p v-if="authStore.isAdmin">
        Manage all events in the system
      </p>
      <p v-else-if="authStore.isOrganizer">
        Manage events you are organizing
      </p>
    </div>

    <!-- Event List View -->
    <div v-if="!selectedEvent" class="events-list">
      <div class="list-header">
        <h2>Your Events</h2>
        <button 
          class="btn-primary" 
          @click="openCreateModal"
        >
          Create New Event
        </button>
      </div>

      <!-- Browser/Filters -->
      <div class="filters-section">
        <div class="filters">
          <input
            v-model="filterLocation"
            placeholder="Filter by location..."
            class="filter-input"
          />
          <input
            v-model="filterName"
            placeholder="Filter by event name..."
            class="filter-input"
          />
          <input
            v-model="filterDate"
            type="date"
            placeholder="Filter by date..."
            class="filter-input"
          />
          <select v-model="filterVisibility" class="filter-input">
            <option value="">All Events</option>
            <option value="public">Public Only</option>
            <option value="private">Private Only</option>
          </select>
        </div>
        <div class="filter-actions">
          <button 
            v-if="hasActiveFilters"
            @click="clearFilters"
            class="btn-secondary clear-filters"
          >
            Clear Filters
          </button>
          <span class="filter-count">
            {{ filteredEvents.length }} of {{ allEvents.length }} events
          </span>
        </div>
      </div>

      <div v-if="loading" class="loading">
        Loading events...
      </div>

      <div v-else-if="error" class="error">
        {{ error }}
      </div>

      <div v-else-if="filteredEvents.length === 0" class="empty-state">
        <p v-if="hasActiveFilters">No events match your filters.</p>
        <p v-else>No events found. Start by creating a new event!</p>
        <button 
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="btn-secondary"
        >
          Clear Filters
        </button>
      </div>

      <div v-else class="events-grid">
        <div 
          v-for="event in filteredEvents" 
          :key="event.id"
          class="event-card"
          @click="selectEvent(event)"
        >
          <div class="event-header">
            <h3>{{ event.name }}</h3>
            <span class="event-date">{{ formatDate(event.start_date) }}</span>
          </div>
          
          <div class="event-details">
            <p class="event-location">
              {{ event.locations.join(', ') }}
            </p>
            <p class="event-participants">
              {{ event.participants.length }} participants
            </p>
            <p class="event-organizers">
              Organized by: {{ event.organizers.join(', ') }}
            </p>
          </div>

          <div class="event-actions">
            <button 
              class="btn-secondary"
              @click.stop="editEvent(event)"
            >
              Edit
            </button>
            <button 
              class="btn-danger"
              @click.stop="deleteEvent(event.id)"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Detail View -->
    <div v-else class="event-detail">
      <div class="detail-header">
        <button class="btn-back" @click="selectedEvent = null">
          Back to Events
        </button>
        <div class="detail-actions">
          <button 
            class="btn-primary"
            @click="editEvent(selectedEvent)"
          >
            Edit Event
          </button>
          <button 
            class="btn-danger"
            @click="deleteEvent(selectedEvent.id)"
          >
            Delete Event
          </button>
        </div>
      </div>

      <div class="event-info">
        <h2>{{ selectedEvent.name }}</h2>
        
        <div class="info-grid">
          <div class="info-section">
            <h3>Date & Time</h3>
            <p>{{ formatDate(selectedEvent.start_date) }}</p>
            <p>{{ selectedEvent.start_time }} - {{ selectedEvent.end_time || 'TBD' }}</p>
            <p v-if="selectedEvent.end_date">
              Until: {{ formatDate(selectedEvent.end_date) }}
            </p>
          </div>

          <div class="info-section">
            <h3>Location</h3>
            <p>{{ selectedEvent.locations.join(', ') }}</p>
          </div>

          <div class="info-section">
            <h3>Organizers</h3>
            <p>{{ selectedEvent.organizers.join(', ') }}</p>
          </div>
        </div>

        <div class="description-section">
          <h3>Description</h3>
          <p>{{ selectedEvent.description }}</p>
        </div>

        <div v-if="selectedEvent.notes.length > 0" class="notes-section">
          <h3>Notes</h3>
          <ul>
            <li v-for="note in selectedEvent.notes" :key="note">
              {{ note }}
            </li>
          </ul>
        </div>

        <div v-if="selectedEvent.images.length > 0" class="images-section">
          <h3>Images</h3>
          <div class="images-grid">
            <img 
              v-for="image in selectedEvent.images" 
              :key="image"
              :src="image"
              :alt="`${selectedEvent.name} image`"
              class="event-image"
            />
          </div>
        </div>
      </div>

      <!-- Participants Management -->
      <div class="participants-section">
        <h3>Participants ({{ selectedEvent.participants.length }})</h3>
        
        <div class="participants-header">
          <button 
            class="btn-primary"
            @click="openAddParticipantModal"
          >
            Add Participant
          </button>
        </div>

        <div v-if="selectedEvent.participants.length === 0" class="empty-participants">
          <p>No participants yet</p>
        </div>

        <div v-else class="participants-list">
          <div 
            v-for="participant in selectedEvent.participants" 
            :key="participant.user_id"
            class="participant-card"
          >
            <div class="participant-info">
              <h4>{{ getUsername(participant.user_id) }}</h4>
              <p class="participant-email">{{ getUserEmail(participant.user_id) }}</p>
              <div v-if="participant.tags.length > 0" class="participant-tags">
                <span 
                  v-for="tag in participant.tags" 
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
            
            <div class="participant-payment">
              <p>Due: ${{ participant.due_payment }}</p>
              <p>Paid: ${{ participant.paid_amount }}</p>
              <p :class="getPaymentStatusClass(participant)">
                {{ getPaymentStatus(participant) }}
              </p>
              <button 
                class="btn-small"
                @click="updateParticipantPayment(participant)"
              >
                Update Payment
              </button>
            </div>

            <button 
              class="btn-danger btn-small"
              @click="removeParticipant(participant.user_id)"
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Event Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <h3>{{ showEditModal ? 'Edit Event' : 'Create New Event' }}</h3>
        
        <EventForm
          ref="eventFormRef"
          :use-textarea="false"
          :use-location-tags="true"
          input-separator=","
          :current-username="authStore.user?.username"
          submit-label="Create Event"
          @submit="handleSaveEvent"
          @cancel="closeModal"
        />
      </div>
    </div>

    <!-- Add Participant Modal -->
    <div v-if="showAddParticipantModal" class="modal-overlay" @click="closeAddParticipantModal">
      <div class="modal" @click.stop>
        <h3>Add Participant</h3>
        
        <form @submit.prevent="addParticipant">
          <div class="form-group">
            <label for="participantUserSearch">Search User</label>
            <div class="select-with-search">
              <input 
                id="participantUserSearch"
                v-model="userSearch" 
                type="text" 
                placeholder="Search by username or email..."
                class="form-input search-input"
                @focus="showUserDropdown = true"
              />
              <div v-if="showUserDropdown && (filteredUsersForAdd.length > 0 || userSearch)" class="dropdown">
                <div 
                  v-for="user in filteredUsersForAdd" 
                  :key="user.id"
                  class="dropdown-item"
                  @click="selectUserForAdd(user)"
                >
                  {{ user.username }} ({{ user.email }})
                </div>
                <div v-if="filteredUsersForAdd.length === 0 && userSearch" class="dropdown-item no-results">
                  No users found
                </div>
              </div>
            </div>
            <p v-if="selectedUserForAdd" class="selected-user-display">
              Selected: <strong>{{ selectedUserForAdd.username }}</strong> ({{ selectedUserForAdd.email }})
            </p>
          </div>

          <div class="form-group">
            <label for="participantDue">Due Payment</label>
            <input 
              id="participantDue"
              v-model.number="participantForm.due_payment" 
              type="number" 
              step="0.01"
              min="0"
              required
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeAddParticipantModal">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="loading || !selectedUserForAdd">
              {{ loading ? 'Adding...' : 'Add Participant' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Update Payment Modal -->
    <div v-if="showUpdatePaymentModal" class="modal-overlay" @click="closeUpdatePaymentModal">
      <div class="modal" @click.stop>
        <h3>Update Payment</h3>
        <p>Participant: {{ getUserDisplay(selectedParticipant?.user_id || '') }}</p>
        
        <form @submit.prevent="savePaymentUpdate">
          <div class="form-group">
            <label for="paidAmount">Paid Amount</label>
            <input 
              id="paidAmount"
              v-model.number="paymentUpdateForm.paid_amount" 
              type="number" 
              step="0.01"
              min="0"
              required
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeUpdatePaymentModal">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
              {{ loading ? 'Updating...' : 'Update Payment' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, reactive, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useEventStore } from '@/stores/events';
import EventForm from '@/components/EventForm.vue';
import type { Event, EventCreate, Participant, UserInfo } from '@/types';
import { eventsAPI, authAPI } from '@/utils/api';

const authStore = useAuthStore();
const eventStore = useEventStore();
const router = useRouter();

// View state
const selectedEvent = ref<Event | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

// Users for participant management
const availableUsers = ref<UserInfo[]>([]);
const userSearch = ref('');
const selectedUserForAdd = ref<UserInfo | null>(null);
const showUserDropdown = ref(false);

// Browser filters
const filterLocation = ref("");
const filterName = ref("");
const filterDate = ref("");
const filterVisibility = ref("");

// Modal state
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showAddParticipantModal = ref(false);
const showUpdatePaymentModal = ref(false);

const eventFormRef = ref<InstanceType<typeof EventForm> | null>(null);

const participantForm = reactive({
  user_id: '',
  due_payment: 0,
  tags: [] as string[]
});

const selectedParticipant = ref<Participant | null>(null);
const paymentUpdateForm = reactive({
  paid_amount: 0
});

// Load available users
const loadUsers = async () => {
  try {
    const users = await authAPI.getUsers();
    availableUsers.value = users.map(user => ({
      id: user.id,
      username: user.username,
      email: user.email
    }));
  } catch (err) {
    console.error('Failed to load users:', err);
  }
};

// Get username by user ID
const getUsername = (userId: string): string => {
  const user = availableUsers.value.find(u => u.id === userId);
  return user ? user.username : userId;
};

// Get email by user ID
const getUserEmail = (userId: string): string => {
  const user = availableUsers.value.find(u => u.id === userId);
  return user ? user.email : '';
};

// Filtered users for add participant (exclude current user and existing participants)
const filteredUsersForAdd = computed(() => {
  if (!selectedEvent.value) return [];
  
  const currentUserId = authStore.user?.id;
  const existingParticipantIds = new Set(selectedEvent.value.participants.map(p => p.user_id));
  
  let filtered = availableUsers.value.filter(user => 
    user.id !== currentUserId && !existingParticipantIds.has(user.id)
  );
  
  if (!userSearch.value.trim()) return filtered;
  
  const searchLower = userSearch.value.toLowerCase().trim();
  return filtered.filter(user => 
    user.username.toLowerCase().includes(searchLower) ||
    (user.email && user.email.toLowerCase().includes(searchLower))
  );
});

// Select user for add participant
const selectUserForAdd = (user: UserInfo) => {
  selectedUserForAdd.value = user;
  userSearch.value = user.username;
  showUserDropdown.value = false;
};

// Computed properties
const allEvents = computed(() => {
  if (!eventStore.events) return [];
  
  return eventStore.events.filter(event => {
    if (authStore.isAdmin) return true; // Admins see all events
    if (authStore.isOrganizer) {
      // Organizers see events they organize
      return event.organizers.includes(authStore.user.username);
    }
    return false;
  });
});

const filteredEvents = computed(() => {
  let filtered = allEvents.value;

  // Filter by location
  if (filterLocation.value) {
    filtered = filtered.filter((event) =>
      event.locations.some((loc) =>
        loc.toLowerCase().includes(filterLocation.value.toLowerCase()),
      ),
    );
  }

  // Filter by event name
  if (filterName.value) {
    filtered = filtered.filter((event) =>
      event.name.toLowerCase().includes(filterName.value.toLowerCase()),
    );
  }

  // Filter by date
  if (filterDate.value) {
    filtered = filtered.filter((event) =>
      event.start_date === filterDate.value ||
      (event.end_date && event.end_date >= filterDate.value && event.start_date <= filterDate.value)
    );
  }

  // Filter by visibility
  if (filterVisibility.value) {
    filtered = filtered.filter((event) =>
      event.visibility === filterVisibility.value
    );
  }

  return filtered;
});

const hasActiveFilters = computed(() => {
  return filterLocation.value || filterName.value || filterDate.value || filterVisibility.value;
});

// Methods
const selectEvent = (event: Event) => {
  router.push(`/event/${event.id}`);
};

const clearFilters = () => {
  filterLocation.value = "";
  filterName.value = "";
  filterDate.value = "";
  filterVisibility.value = "";
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString();
};

const getPaymentStatus = (participant: Participant) => {
  if (participant.paid_amount >= participant.due_payment) {
    return 'Paid in full';
  } else if (participant.paid_amount > 0) {
    return 'Partially paid';
  }
  return 'Unpaid';
};

const getPaymentStatusClass = (participant: Participant) => {
  if (participant.paid_amount >= participant.due_payment) {
    return 'status-paid';
  } else if (participant.paid_amount > 0) {
    return 'status-partial';
  }
  return 'status-unpaid';
};

const getUserDisplay = (userId: string) => {
  const user = availableUsers.value.find(u => u.id === userId);
  if (user) {
    return `${user.username} (${user.email})`;
  }
  return userId;
};

// Event management
const editEvent = (event: Event) => {
  router.push(`/event/${event.id}`);
};

const deleteEvent = async (eventId: string) => {
  if (!confirm('Are you sure you want to delete this event?')) return;
  
  try {
    loading.value = true;
    await eventsAPI.deleteEvent(eventId);
    await eventStore.fetchEvents();
    if (selectedEvent.value?.id === eventId) {
      selectedEvent.value = null;
    }
  } catch (err) {
    error.value = 'Failed to delete event';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const handleSaveEvent = async (eventData: EventCreate) => {
  try {
    loading.value = true;
    console.log('Saving event:', eventData);
    
    if (showEditModal.value && selectedEvent.value) {
      await eventsAPI.updateEvent(selectedEvent.value.id, eventData);
    } else {
      await eventsAPI.createEvent(eventData);
    }
    
    await eventStore.fetchEvents();
    closeModal();
  } catch (err: any) {
    const detail = err.response?.data?.detail;
    if (Array.isArray(detail)) {
      error.value = detail.map((e: any) => `${e.loc?.join('.')}: ${e.msg}`).join(', ');
    } else {
      error.value = detail || 'Failed to save event';
    }
    console.error(err);
  } finally {
    loading.value = false;
  }
};

// Modal management
const openCreateModal = async () => {
  showCreateModal.value = true;
  await nextTick();
  if (authStore.user?.username) {
    eventFormRef.value?.setInitialOrganizers(authStore.user.username);
  }
};

const openAddParticipantModal = async () => {
  await loadUsers();
  showAddParticipantModal.value = true;
};

const closeModal = () => {
  showCreateModal.value = false;
  showEditModal.value = false;
  eventFormRef.value?.reset();
};

// Participant management
const addParticipant = async () => {
  if (!selectedUserForAdd.value) return;
  
  try {
    loading.value = true;
    
    participantForm.user_id = selectedUserForAdd.value.id;

    if (selectedEvent.value) {
      await eventsAPI.addParticipant(selectedEvent.value.id, participantForm);
      const updatedEvent = await eventsAPI.getEvent(selectedEvent.value.id);
      selectedEvent.value = updatedEvent;
    }
    
    closeAddParticipantModal();
  } catch (err) {
    error.value = 'Failed to add participant';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const removeParticipant = async (userId: string) => {
  if (!confirm('Are you sure you want to remove this participant?')) return;
  
  try {
    loading.value = true;
    
    if (selectedEvent.value) {
      await eventsAPI.removeParticipant(selectedEvent.value.id, userId);
      const updatedEvent = await eventsAPI.getEvent(selectedEvent.value.id);
      selectedEvent.value = updatedEvent;
    }
  } catch (err) {
    error.value = 'Failed to remove participant';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const updateParticipantPayment = (participant: Participant) => {
  selectedParticipant.value = participant;
  paymentUpdateForm.paid_amount = participant.paid_amount;
  showUpdatePaymentModal.value = true;
};

const savePaymentUpdate = async () => {
  try {
    loading.value = true;
    
    if (selectedEvent.value && selectedParticipant.value) {
      await eventsAPI.updateParticipantPayment(
        selectedEvent.value.id,
        selectedParticipant.value.user_id,
        paymentUpdateForm.paid_amount
      );
      const updatedEvent = await eventsAPI.getEvent(selectedEvent.value.id);
      selectedEvent.value = updatedEvent;
    }
    
    closeUpdatePaymentModal();
  } catch (err) {
    error.value = 'Failed to update payment';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const closeAddParticipantModal = () => {
  showAddParticipantModal.value = false;
  showUserDropdown.value = false;
  resetParticipantForm();
};

const closeUpdatePaymentModal = () => {
  showUpdatePaymentModal.value = false;
  selectedParticipant.value = null;
  paymentUpdateForm.paid_amount = 0;
};

const resetParticipantForm = () => {
  selectedUserForAdd.value = null;
  userSearch.value = '';
  Object.assign(participantForm, {
    user_id: '',
    due_payment: 0,
    tags: []
  });
};

// Handle click outside to close dropdown
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest('.select-with-search')) {
    showUserDropdown.value = false;
  }
};

// Lifecycle
onMounted(async () => {
  try {
    loading.value = true;
    await Promise.all([
      eventStore.fetchEvents(),
      loadUsers()
    ]);
    document.addEventListener('click', handleClickOutside);
  } catch (err) {
    error.value = 'Failed to load events';
    console.error(err);
  } finally {
    loading.value = false;
  }
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.organizer-view {
  min-height: calc(100vh - 60px);
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--white) 100%);
}

.organizer-header {
  margin-bottom: 2rem;
  animation: fadeInUp 0.6s ease-out;
}

.organizer-header h1 {
  color: var(--gray-900);
  margin-bottom: 0.5rem;
  font-size: 2rem;
  font-weight: 700;
}

.organizer-header p {
  color: var(--gray-600);
  font-size: 1.1rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.list-header h2 {
  color: #2c3e50;
}

.filters-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  border: 1px solid #e9ecef;
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.filter-input {
  flex: 1;
  min-width: 200px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.filter-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.clear-filters {
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
}

.filter-count {
  color: #6c757d;
  font-size: 0.9rem;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.event-card {
  background: var(--white);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
  box-shadow: var(--shadow-md);
  cursor: pointer;
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
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-200);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
}

.event-header h3 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.3rem;
}

.event-date {
  color: #667eea;
  font-weight: 600;
  font-size: 0.9rem;
}

.event-details p {
  margin: 0.5rem 0;
  color: #7f8c8d;
  font-size: 0.95rem;
}

.event-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #ecf0f1;
}

.btn-back {
  background: none;
  border: none;
  color: #667eea;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.5rem;
}

.btn-back:hover {
  text-decoration: underline;
}

.detail-actions {
  display: flex;
  gap: 0.5rem;
}

.event-info h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.info-section h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.info-section p {
  color: #7f8c8d;
  margin: 0.3rem 0;
}

.description-section,
.notes-section,
.images-section {
  margin-bottom: 2rem;
}

.description-section h3,
.notes-section h3,
.images-section h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.notes-section ul {
  list-style: none;
  padding: 0;
}

.notes-section li {
  background: #f8f9fa;
  padding: 0.5rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  border-left: 4px solid #667eea;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.event-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
}

.participants-section {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 12px;
  margin-top: 2rem;
}

.participants-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.participants-section h3 {
  color: #2c3e50;
  margin: 0;
}

.participants-list {
  display: grid;
  gap: 1rem;
}

.participant-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  display: flex;
  gap: 1.5rem;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.participant-card .participant-info {
  flex: 1;
}

.participant-card .participant-payment {
  flex-shrink: 0;
}

.participant-card .btn-danger {
  flex-shrink: 0;
}

.participant-info h4 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.participant-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.participant-payment {
  text-align: center;
  margin: 0 2rem;
}

.participant-payment p {
  margin: 0.2rem 0;
  font-size: 0.9rem;
}

.status-paid {
  color: #27ae60;
  font-weight: 600;
}

.status-partial {
  color: #f39c12;
  font-weight: 600;
}

.status-unpaid {
  color: #e74c3c;
  font-weight: 600;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
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

.modal h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.select-with-search {
  position: relative;
}

.search-input {
  width: 100%;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
}

.dropdown-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.dropdown-item.no-results {
  color: #999;
  cursor: default;
}

.dropdown-item.no-results:hover {
  background-color: transparent;
}

.selected-user-display {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #e3f2fd;
  border-radius: 6px;
  color: #1976d2;
}

.participant-email {
  font-size: 0.875rem;
  color: #666;
  margin: 0.25rem 0 0 0;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
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
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.remove-btn {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  line-height: 1;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

/* Button styles */
.btn-primary {
  background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  color: var(--primary-600);
  border: 2px solid var(--primary-200);
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--primary-50);
  border-color: var(--primary-300);
}

.btn-danger {
  background: var(--error);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

/* Utility styles */
.loading {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

.error {
  background: #ffeaa7;
  color: #d63031;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.empty-state,
.empty-participants {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

@media (max-width: 768px) {
  .organizer-view {
    padding: 1rem;
  }
  
  .filters {
    flex-direction: column;
  }
  
  .filter-input {
    min-width: auto;
  }
  
  .filter-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .events-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .participant-card {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .participant-payment {
    margin: 0;
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