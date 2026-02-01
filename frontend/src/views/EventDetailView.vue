<template>
  <div class="event-detail-view">
    <div class="detail-header">
      <button class="btn-back" @click="goBack">
        ← Back to Events
      </button>
      <div class="header-actions">
        <button 
          class="btn-primary"
          @click="toggleEditMode"
        >
          {{ isEditMode ? 'View Mode' : 'Edit Event' }}
        </button>
        <button 
          class="btn-danger"
          @click="confirmDelete"
        >
          Delete Event
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      Loading event details...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="!event" class="not-found">
      Event not found
    </div>

    <div v-else class="event-content">
      <!-- View Mode -->
      <div v-if="!isEditMode" class="view-mode">
        <div class="event-hero">
          <div class="event-title-section">
            <h1 class="event-title">{{ event.name }}</h1>
            <div class="event-meta">
              <span class="meta-item">
                📅 {{ formatDate(event.start_date) }}
              </span>
              <span class="meta-item">
                🕐 {{ event.start_time }} - {{ event.end_time || 'TBD' }}
              </span>
              <span v-if="event.end_date" class="meta-item">
                📅 Until: {{ formatDate(event.end_date) }}
              </span>
            </div>
          </div>
        </div>

        <div class="event-details-grid">
          <div class="detail-card">
            <h3>📍 Location</h3>
            <div class="locations-list">
              <span 
                v-for="location in event.locations" 
                :key="location"
                class="location-chip"
              >
                {{ location }}
              </span>
            </div>
          </div>

          <div class="detail-card">
            <h3>🎯 Organizers</h3>
            <div class="organizers-list">
              <span 
                v-for="organizer in event.organizers" 
                :key="organizer"
                class="organizer-chip"
              >
                {{ organizer }}
              </span>
            </div>
          </div>

          <div class="detail-card full-width">
            <h3>📝 Description</h3>
            <p class="description">{{ event.description }}</p>
          </div>

          <div v-if="event.notes.length > 0" class="detail-card full-width">
            <h3>📋 Notes</h3>
            <div class="notes-list">
              <div 
                v-for="note in event.notes" 
                :key="note"
                class="note-item"
              >
                {{ note }}
              </div>
            </div>
          </div>

          <div v-if="event.images.length > 0" class="detail-card full-width">
            <h3>🖼️ Images</h3>
            <div class="images-gallery">
              <img 
                v-for="image in event.images" 
                :key="image"
                :src="image"
                :alt="`${event.name} image`"
                class="event-image"
                @click="openImageModal(image)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Mode -->
      <div v-else class="edit-mode">
        <form @submit.prevent="saveEvent" class="event-form">
          <div class="form-section">
            <h3>Basic Information</h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="eventName">Event Name</label>
                <input 
                  id="eventName"
                  v-model="eventForm.name" 
                  type="text" 
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="eventStartDate">Start Date</label>
                <input 
                  id="eventStartDate"
                  v-model="eventForm.start_date" 
                  type="date" 
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="eventStartTime">Start Time</label>
                <input 
                  id="eventStartTime"
                  v-model="eventForm.start_time" 
                  type="time" 
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="eventEndDate">End Date (optional)</label>
                <input 
                  id="eventEndDate"
                  v-model="eventForm.end_date" 
                  type="date"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="eventEndTime">End Time (optional)</label>
                <input 
                  id="eventEndTime"
                  v-model="eventForm.end_time" 
                  type="time"
                  class="form-input"
                />
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>Description</h3>
            <div class="form-group">
              <textarea 
                v-model="eventForm.description" 
                required
                class="form-textarea"
                rows="4"
                placeholder="Describe your event..."
              ></textarea>
            </div>
          </div>

          <div class="form-section">
            <h3>Locations</h3>
            <div class="locations-form">
              <div class="location-input-group">
                <input 
                  v-model="locationInput" 
                  type="text" 
                  placeholder="Enter location"
                  class="form-input"
                  @keyup.enter="addLocation"
                />
                <button 
                  type="button"
                  @click="addLocation"
                  class="btn-secondary"
                >
                  Add
                </button>
              </div>
              <div v-if="eventForm.locations.length > 0" class="locations-list-form">
                <span 
                  v-for="(loc, index) in eventForm.locations" 
                  :key="index"
                  class="location-tag"
                >
                  {{ loc }}
                  <button 
                    type="button"
                    class="remove-btn"
                    @click="removeLocation(index)"
                  >
                    ×
                  </button>
                </span>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>Notes</h3>
            <div class="form-group">
              <textarea 
                v-model="notesInput" 
                class="form-textarea"
                rows="4"
                placeholder="Enter notes, one per line"
              ></textarea>
            </div>
          </div>

          <div class="form-actions">
            <button 
              type="button" 
              class="btn-secondary"
              @click="cancelEdit"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn-primary"
              :disabled="saving"
            >
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Participants Section (always visible) -->
      <div class="participants-section">
        <div class="participants-header">
          <h3>👥 Participants ({{ event.participants.length }})</h3>
          <button 
            class="btn-primary"
            @click="showAddParticipant = true"
          >
            Add Participant
          </button>
        </div>

        <div v-if="event.participants.length === 0" class="empty-participants">
          <p>No participants yet</p>
        </div>

        <div v-else class="participants-grid">
          <div 
            v-for="participant in event.participants" 
            :key="participant.user_id"
            class="participant-card"
          >
            <div class="participant-header">
              <h4>{{ participant.user_id }}</h4>
              <button 
                class="btn-danger btn-small"
                @click="removeParticipant(participant.user_id)"
              >
                Remove
              </button>
            </div>
            
            <div class="participant-body">
              <div v-if="participant.tags.length > 0" class="participant-tags">
                <span 
                  v-for="tag in participant.tags" 
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
              </div>
              
              <div class="payment-info">
                <div class="payment-row">
                  <span>Due:</span>
                  <span class="amount due">${{ participant.due_payment }}</span>
                </div>
                <div class="payment-row">
                  <span>Paid:</span>
                  <span class="amount paid">${{ participant.paid_amount }}</span>
                </div>
                <div class="payment-status" :class="getPaymentStatusClass(participant)">
                  {{ getPaymentStatus(participant) }}
                </div>
              </div>
              
              <button 
                class="btn-secondary btn-small btn-full"
                @click="openPaymentModal(participant)"
              >
                Update Payment
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Participant Modal -->
    <div v-if="showAddParticipant" class="modal-overlay" @click="closeAddParticipant">
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
              class="form-input"
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
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="participantTags">Tags (comma-separated)</label>
            <input 
              id="participantTags"
              v-model="participantTagsInput" 
              type="text" 
              placeholder="tag1, tag2, tag3"
              class="form-input"
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeAddParticipant">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Adding...' : 'Add Participant' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Payment Update Modal -->
    <div v-if="showPaymentModal" class="modal-overlay" @click="closePaymentModal">
      <div class="modal" @click.stop>
        <h3>Update Payment</h3>
        <p>Participant: {{ selectedParticipant?.user_id }}</p>
        
        <form @submit.prevent="updatePayment">
          <div class="form-group">
            <label for="paidAmount">Paid Amount</label>
            <input 
              id="paidAmount"
              v-model.number="paymentForm.paid_amount" 
              type="number" 
              step="0.01"
              min="0"
              required
              class="form-input"
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closePaymentModal">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Updating...' : 'Update Payment' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Image Modal -->
    <div v-if="selectedImage" class="image-modal-overlay" @click="closeImageModal">
      <div class="image-modal" @click.stop>
        <button class="close-image" @click="closeImageModal">×</button>
        <img :src="selectedImage" :alt="event?.name" class="modal-image" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { eventsAPI } from '@/utils/api';
import type { Event, Participant } from '@/types';

const route = useRoute();
const router = useRouter();

const event = ref<Event | null>(null);
const loading = ref(true);
const saving = ref(false);
const error = ref<string | null>(null);

const isEditMode = ref(false);
const showAddParticipant = ref(false);
const showPaymentModal = ref(false);
const selectedImage = ref<string | null>(null);

const eventForm = reactive({
  name: '',
  description: '',
  locations: [] as string[],
  start_date: '',
  end_date: '',
  start_time: '',
  end_time: '',
  notes: [] as string[]
});

const locationInput = ref('');
const notesInput = ref('');

const participantForm = reactive({
  user_id: '',
  due_payment: 0,
  tags: [] as string[]
});

const participantTagsInput = ref('');
const selectedParticipant = ref<Participant | null>(null);
const paymentForm = reactive({
  paid_amount: 0
});

const loadEvent = async () => {
  try {
    loading.value = true;
    const eventId = route.params.id as string;
    const eventData = await eventsAPI.getEvent(eventId);
    event.value = eventData;
    resetForm();
  } catch (err) {
    error.value = 'Failed to load event';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  if (!event.value) return;
  
  Object.assign(eventForm, {
    name: event.value.name,
    description: event.value.description,
    locations: [...event.value.locations],
    start_date: event.value.start_date,
    end_date: event.value.end_date || '',
    start_time: event.value.start_time,
    end_time: event.value.end_time || '',
    notes: [...event.value.notes]
  });
  
  notesInput.value = event.value.notes.join('\n');
};

const toggleEditMode = () => {
  if (isEditMode.value) {
    resetForm();
  }
  isEditMode.value = !isEditMode.value;
};

const cancelEdit = () => {
  isEditMode.value = false;
  resetForm();
};

const saveEvent = async () => {
  if (!event.value) return;
  
  try {
    saving.value = true;
    
    eventForm.notes = notesInput.value
      .split('\n')
      .map(note => note.trim())
      .filter(note => note.length > 0);

    await eventsAPI.updateEvent(event.value.id, eventForm);
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
    
    isEditMode.value = false;
  } catch (err) {
    error.value = 'Failed to save event';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const confirmDelete = () => {
  if (!event.value) return;
  if (confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
    deleteEvent();
  }
};

const deleteEvent = async () => {
  if (!event.value) return;
  
  try {
    saving.value = true;
    await eventsAPI.deleteEvent(event.value.id);
    router.push('/organizer');
  } catch (err) {
    error.value = 'Failed to delete event';
    console.error(err);
    saving.value = false;
  }
};

const addLocation = () => {
  if (locationInput.value.trim()) {
    eventForm.locations.push(locationInput.value.trim());
    locationInput.value = '';
  }
};

const removeLocation = (index: number) => {
  eventForm.locations.splice(index, 1);
};

const goBack = () => {
  router.push('/organizer');
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString();
};

const getPaymentStatus = (participant: Participant) => {
  if (participant.paid_amount >= participant.due_payment) {
    return '✅ Paid in full';
  } else if (participant.paid_amount > 0) {
    return '⏳ Partially paid';
  }
  return '❌ Unpaid';
};

const getPaymentStatusClass = (participant: Participant) => {
  if (participant.paid_amount >= participant.due_payment) {
    return 'status-paid';
  } else if (participant.paid_amount > 0) {
    return 'status-partial';
  }
  return 'status-unpaid';
};

const addParticipant = async () => {
  if (!event.value) return;
  
  try {
    saving.value = true;
    
    participantForm.tags = participantTagsInput.value
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0);

    await eventsAPI.addParticipant(event.value.id, participantForm);
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
    
    closeAddParticipant();
  } catch (err) {
    error.value = 'Failed to add participant';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const removeParticipant = async (userId: string) => {
  if (!event.value) return;
  if (!confirm('Are you sure you want to remove this participant?')) return;
  
  try {
    saving.value = true;
    
    await eventsAPI.removeParticipant(event.value.id, userId);
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
  } catch (err) {
    error.value = 'Failed to remove participant';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const openPaymentModal = (participant: Participant) => {
  selectedParticipant.value = participant;
  paymentForm.paid_amount = participant.paid_amount;
  showPaymentModal.value = true;
};

const updatePayment = async () => {
  if (!event.value || !selectedParticipant.value) return;
  
  try {
    saving.value = true;
    
    await eventsAPI.updateParticipantPayment(
      event.value.id,
      selectedParticipant.value.user_id,
      paymentForm.paid_amount
    );
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
    
    closePaymentModal();
  } catch (err) {
    error.value = 'Failed to update payment';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const closeAddParticipant = () => {
  showAddParticipant.value = false;
  Object.assign(participantForm, {
    user_id: '',
    due_payment: 0,
    tags: []
  });
  participantTagsInput.value = '';
};

const closePaymentModal = () => {
  showPaymentModal.value = false;
  selectedParticipant.value = null;
  paymentForm.paid_amount = 0;
};

const openImageModal = (image: string) => {
  selectedImage.value = image;
};

const closeImageModal = () => {
  selectedImage.value = null;
};

onMounted(() => {
  loadEvent();
});
</script>

<style scoped>
.event-detail-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
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
  text-decoration: none;
}

.btn-back:hover {
  text-decoration: underline;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.event-hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  text-align: center;
}

.event-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.event-meta {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 1.1rem;
  opacity: 0.95;
}

.event-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.detail-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: 1px solid #ecf0f1;
}

.detail-card.full-width {
  grid-column: 1 / -1;
}

.detail-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.locations-list,
.organizers-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.location-chip,
.organizer-chip {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.organizer-chip {
  background: #f3e5f5;
  color: #7b1fa2;
}

.description {
  line-height: 1.6;
  color: #2c3e50;
  font-size: 1.05rem;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.note-item {
  background: #f8f9fa;
  padding: 0.8rem 1.2rem;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  color: #2c3e50;
  line-height: 1.5;
}

.images-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.event-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-image:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.edit-mode {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.form-section {
  margin-bottom: 2rem;
}

.form-section h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #ecf0f1;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
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

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
}

.location-input-group {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.location-input-group .form-input {
  flex: 1;
}

.locations-list-form {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #ecf0f1;
}

.participants-section {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #ecf0f1;
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
  font-size: 1.3rem;
}

.participants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.participant-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #ecf0f1;
}

.participant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.participant-header h4 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.1rem;
}

.participant-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.participant-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  background: #e8f5e8;
  color: #2e7d32;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.payment-info {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
}

.payment-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.3rem;
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

.payment-status {
  text-align: center;
  padding: 0.5rem;
  border-radius: 6px;
  font-weight: 600;
  margin-top: 0.5rem;
}

.status-paid {
  background: #d4edda;
  color: #155724;
}

.status-partial {
  background: #fff3cd;
  color: #856404;
}

.status-unpaid {
  background: #f8d7da;
  color: #721c24;
}

.btn-full {
  width: 100%;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

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
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.image-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}

.image-modal {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.close-image {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
  padding: 0.5rem;
}

.modal-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

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

.loading,
.error,
.not-found {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
}

.error {
  background: #ffeaa7;
  color: #d63031;
  border-radius: 8px;
}

.empty-participants {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

@media (max-width: 768px) {
  .event-detail-view {
    padding: 1rem;
  }
  
  .detail-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .event-hero {
    padding: 2rem 1rem;
  }
  
  .event-title {
    font-size: 2rem;
  }
  
  .event-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .event-details-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .location-input-group {
    flex-direction: column;
  }
  
  .participants-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .participants-grid {
    grid-template-columns: 1fr;
  }
}
</style>