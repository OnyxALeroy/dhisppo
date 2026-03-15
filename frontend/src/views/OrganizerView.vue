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
              📍 {{ event.locations.join(', ') }}
            </p>
            <p class="event-participants">
              👥 {{ event.participants.length }} participants
            </p>
            <p class="event-organizers">
              🎯 Organized by: {{ event.organizers.join(', ') }}
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
          ← Back to Events
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
            <p>📅 {{ formatDate(selectedEvent.start_date) }}</p>
            <p>🕐 {{ selectedEvent.start_time }} - {{ selectedEvent.end_time || 'TBD' }}</p>
            <p v-if="selectedEvent.end_date">
              📅 Until: {{ formatDate(selectedEvent.end_date) }}
            </p>
          </div>

          <div class="info-section">
            <h3>Location</h3>
            <p>📍 {{ selectedEvent.locations.join(', ') }}</p>
          </div>

          <div class="info-section">
            <h3>Organizers</h3>
            <p>🎯 {{ selectedEvent.organizers.join(', ') }}</p>
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
            @click="showAddParticipantModal = true"
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
              <h4>{{ participant.user_id }}</h4>
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
            <label for="participantUserId">User ID</label>
            <input 
              id="participantUserId"
              v-model="participantForm.user_id" 
              type="text" 
              required
            />
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

          <div class="form-group">
            <label for="participantTags">Tags (comma-separated)</label>
            <input 
              id="participantTags"
              v-model="participantTagsInput" 
              type="text" 
              placeholder="tag1, tag2, tag3"
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeAddParticipantModal">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
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
        <p>Participant: {{ selectedParticipant?.user_id }}</p>
        
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
import { ref, computed, onMounted, reactive, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useEventStore } from '@/stores/events';
import EventForm from '@/components/EventForm.vue';
import type { Event, EventCreate, Participant } from '@/types';
import { eventsAPI } from '@/utils/api';

const authStore = useAuthStore();
const eventStore = useEventStore();
const router = useRouter();

// View state
const selectedEvent = ref<Event | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

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

const participantTagsInput = ref('');

const selectedParticipant = ref<Participant | null>(null);
const paymentUpdateForm = reactive({
  paid_amount: 0
});

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

const closeModal = () => {
  showCreateModal.value = false;
  showEditModal.value = false;
  eventFormRef.value?.reset();
};

// Participant management
const addParticipant = async () => {
  try {
    loading.value = true;
    
    // Process tags
    participantForm.tags = participantTagsInput.value
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0);

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
  resetParticipantForm();
};

const closeUpdatePaymentModal = () => {
  showUpdatePaymentModal.value = false;
  selectedParticipant.value = null;
  paymentUpdateForm.paid_amount = 0;
};

const resetParticipantForm = () => {
  Object.assign(participantForm, {
    user_id: '',
    due_payment: 0,
    tags: []
  });
  participantTagsInput.value = '';
};

// Lifecycle
onMounted(async () => {
  try {
    loading.value = true;
    await eventStore.fetchEvents();
  } catch (err) {
    error.value = 'Failed to load events';
    console.error(err);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.organizer-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.organizer-header {
  margin-bottom: 2rem;
}

.organizer-header h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.organizer-header p {
  color: #7f8c8d;
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
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
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
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: opacity 0.2s;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: #d5dbdd;
}

.btn-danger {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: opacity 0.2s;
}

.btn-danger:hover {
  opacity: 0.9;
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
</style>