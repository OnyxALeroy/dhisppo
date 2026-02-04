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
          <h3>👥 Participants ({{ (event.participants || []).length }})</h3>
          <button 
            class="btn-primary"
            @click="showAddParticipant = true"
          >
            Add Participant
          </button>
        </div>

        <div v-if="!event.participants || event.participants.length === 0" class="empty-participants">
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

      <!-- Payments Section (always visible) -->
      <div class="payments-section">
        <div class="payments-header">
          <h3>💳 Payments ({{ (event.payments || []).length }})</h3>
          <button 
            class="btn-primary"
            @click="showAddPayment = true"
          >
            Add Payment
          </button>
        </div>

        <div v-if="!event.payments || event.payments.length === 0" class="empty-payments">
          <p>No payments yet</p>
        </div>

        <div v-else class="payments-grid">
          <div 
            v-for="payment in event.payments" 
            :key="payment.id"
            class="payment-card"
          >
            <div class="payment-header">
              <h4>{{ payment.title }}</h4>
              <button 
                class="btn-danger btn-small"
                @click="confirmDeletePayment(payment)"
              >
                Delete
              </button>
            </div>
            
            <div class="payment-body">
              <div class="payment-amount">
                <span class="amount-label">Amount:</span>
                <span class="amount-value">${{ payment.amount.toFixed(2) }}</span>
              </div>
              
              <div class="payment-participants">
                <div class="payment-participant">
                  <span class="participant-label">From:</span>
                  <span class="participant-name">{{ payment.sender.username }}</span>
                </div>
                <div class="payment-participant">
                  <span class="participant-label">To:</span>
                  <span class="participant-name">{{ payment.receiver.username }}</span>
                </div>
              </div>
              
              <div class="payment-date">
                <span class="date-label">Date:</span>
                <span class="date-value">{{ formatDate(payment.created_at) }}</span>
              </div>
              
              <button 
                class="btn-secondary btn-small btn-full"
                @click="openEditPaymentModal(payment)"
              >
                Edit Payment
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

    <!-- Add Payment Modal -->
    <div v-if="showAddPayment" class="modal-overlay" @click="closeAddPayment">
      <div class="modal" @click.stop>
        <h3>Add Payment</h3>
        <form @submit.prevent="addPayment">
          <div class="form-group">
            <label for="paymentSender">Sender</label>
            <div class="select-with-search">
              <input 
                id="paymentSender"
                v-model="senderSearch" 
                type="text" 
                placeholder="Search sender..."
                class="form-input search-input"
                @focus="showSenderDropdown = true"
              />
              <div v-if="showSenderDropdown && (filteredSenders.length > 0 || senderSearch)" class="dropdown">
                <div 
                  v-for="user in filteredSenders" 
                  :key="user.id"
                  class="dropdown-item"
                  @click="selectSender(user)"
                >
                  {{ user.username }}
                </div>
                <div v-if="filteredSenders.length === 0 && senderSearch" class="dropdown-item no-results">
                  No users found
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label for="paymentReceiver">Receiver</label>
            <div class="select-with-search">
              <input 
                id="paymentReceiver"
                v-model="receiverSearch" 
                type="text" 
                placeholder="Search receiver..."
                class="form-input search-input"
                @focus="showReceiverDropdown = true"
              />
              <div v-if="showReceiverDropdown && (filteredReceivers.length > 0 || receiverSearch)" class="dropdown">
                <div 
                  v-for="user in filteredReceivers" 
                  :key="user.id"
                  class="dropdown-item"
                  @click="selectReceiver(user)"
                >
                  {{ user.username }}
                </div>
                <div v-if="filteredReceivers.length === 0 && receiverSearch" class="dropdown-item no-results">
                  No users found
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label for="paymentAmount">Amount</label>
            <input 
              id="paymentAmount"
              v-model.number="paymentForm.amount" 
              type="number" 
              step="0.01"
              min="0"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="paymentTitle">Title/Description</label>
            <input 
              id="paymentTitle"
              v-model="paymentForm.title" 
              type="text" 
              required
              class="form-input"
              placeholder="Payment description"
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeAddPayment">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Adding...' : 'Add Payment' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Payment Modal -->
    <div v-if="showEditPayment" class="modal-overlay" @click="closeEditPayment">
      <div class="modal" @click.stop>
        <h3>Edit Payment</h3>
        <p>Original: {{ selectedPayment?.title }}</p>
        
        <form @submit.prevent="editPayment">
          <div class="form-group">
            <label for="editPaymentAmount">Amount</label>
            <input 
              id="editPaymentAmount"
              v-model.number="editPaymentForm.amount" 
              type="number" 
              step="0.01"
              min="0"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="editPaymentTitle">Title/Description</label>
            <input 
              id="editPaymentTitle"
              v-model="editPaymentForm.title" 
              type="text" 
              required
              class="form-input"
              placeholder="Payment description"
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeEditPayment">
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
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { eventsAPI, paymentsAPI, authAPI } from '@/utils/api';
import type { Event, Participant, Payment, UserInfo } from '@/types';

const route = useRoute();
const router = useRouter();

const event = ref<Event | null>(null);
const loading = ref(true);
const saving = ref(false);
const error = ref<string | null>(null);

const isEditMode = ref(false);
const showAddParticipant = ref(false);
const showPaymentModal = ref(false);
const showAddPayment = ref(false);
const showEditPayment = ref(false);
const selectedImage = ref<string | null>(null);
const availableUsers = ref<UserInfo[]>([]);

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

const paymentCreateForm = reactive({
  sender: null as UserInfo | null,
  receiver: null as UserInfo | null,
  amount: 0,
  title: ''
});

const senderSearch = ref('');
const receiverSearch = ref('');
const showSenderDropdown = ref(false);
const showReceiverDropdown = ref(false);

const selectedPayment = ref<Payment | null>(null);
const editPaymentForm = reactive({
  amount: 0,
  title: ''
});

const loadEvent = async () => {
  try {
    loading.value = true;
    const eventId = route.params.id as string;
    const eventData = await eventsAPI.getEvent(eventId);
    // Ensure arrays exist
    if (!eventData.payments) {
      eventData.payments = [];
    }
    if (!eventData.participants) {
      eventData.participants = [];
    }
    if (!eventData.notes) {
      eventData.notes = [];
    }
    if (!eventData.images) {
      eventData.images = [];
    }
    if (!eventData.locations) {
      eventData.locations = [];
    }
    event.value = eventData;
    await loadAvailableUsers();
    resetForm();
  } catch (err) {
    error.value = 'Failed to load event';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const loadAvailableUsers = async () => {
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
    notes: [...(event.value.notes || [])]
  });
  
  notesInput.value = (event.value.notes || []).join('\n');
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

const addPayment = async () => {
  if (!event.value || !paymentCreateForm.sender || !paymentCreateForm.receiver) return;
  
  try {
    saving.value = true;
    
    await paymentsAPI.createPayment(event.value.id, {
      sender: paymentCreateForm.sender,
      receiver: paymentCreateForm.receiver,
      amount: paymentCreateForm.amount,
      title: paymentCreateForm.title
    });
    
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
    
    closeAddPayment();
  } catch (err) {
    error.value = 'Failed to add payment';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const openEditPaymentModal = (payment: Payment) => {
  selectedPayment.value = payment;
  editPaymentForm.amount = payment.amount;
  editPaymentForm.title = payment.title;
  showEditPayment.value = true;
};

const editPayment = async () => {
  if (!event.value || !selectedPayment.value) return;
  
  try {
    saving.value = true;
    
    await paymentsAPI.updatePayment(event.value.id, selectedPayment.value.id, {
      amount: editPaymentForm.amount,
      title: editPaymentForm.title
    });
    
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
    
    closeEditPayment();
  } catch (err) {
    error.value = 'Failed to update payment';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const confirmDeletePayment = (payment: Payment) => {
  if (!event.value) return;
  if (confirm(`Are you sure you want to delete this payment: "${payment.title}"?`)) {
    deletePayment(payment.id);
  }
};

const deletePayment = async (paymentId: string) => {
  if (!event.value) return;
  
  try {
    saving.value = true;
    
    await paymentsAPI.deletePayment(event.value.id, paymentId);
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
  } catch (err) {
    error.value = 'Failed to delete payment';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const closeAddPayment = () => {
  showAddPayment.value = false;
  Object.assign(paymentCreateForm, {
    sender: null,
    receiver: null,
    amount: 0,
    title: ''
  });
  senderSearch.value = '';
  receiverSearch.value = '';
  showSenderDropdown.value = false;
  showReceiverDropdown.value = false;
};

const closeEditPayment = () => {
  showEditPayment.value = false;
  selectedPayment.value = null;
  Object.assign(editPaymentForm, {
    amount: 0,
    title: ''
  });
};

const filteredSenders = computed(() => {
  if (!senderSearch.value) return availableUsers.value;
  return availableUsers.value.filter(user => 
    user.username.toLowerCase().includes(senderSearch.value.toLowerCase()) ||
    user.email.toLowerCase().includes(senderSearch.value.toLowerCase())
  );
});

const filteredReceivers = computed(() => {
  if (!receiverSearch.value) return availableUsers.value;
  return availableUsers.value.filter(user => 
    user.username.toLowerCase().includes(receiverSearch.value.toLowerCase()) ||
    user.email.toLowerCase().includes(receiverSearch.value.toLowerCase())
  );
});

const selectSender = (user: UserInfo) => {
  paymentCreateForm.sender = user;
  senderSearch.value = user.username;
  showSenderDropdown.value = false;
};

const selectReceiver = (user: UserInfo) => {
  paymentCreateForm.receiver = user;
  receiverSearch.value = user.username;
  showReceiverDropdown.value = false;
};

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest('.select-with-search')) {
    showSenderDropdown.value = false;
    showReceiverDropdown.value = false;
  }
};

onMounted(() => {
  loadEvent();
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
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

.payments-section {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #ecf0f1;
  margin-top: 2rem;
}

.payments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.payments-section h3 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.3rem;
}

.payments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1rem;
}

.payment-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #ecf0f1;
}

.payment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.payment-header h4 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.payment-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.payment-amount {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #e8f5e8;
  border-radius: 6px;
}

.amount-label {
  font-weight: 500;
  color: #2e7d32;
}

.amount-value {
  font-weight: 700;
  color: #2e7d32;
  font-size: 1.2rem;
}

.payment-participants {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.payment-participant {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.participant-label {
  font-weight: 500;
  color: #666;
  font-size: 0.9rem;
}

.participant-name {
  font-weight: 600;
  color: #2c3e50;
}

.payment-date {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #666;
}

.date-label {
  font-weight: 500;
}

.date-value {
  color: #7f8c8d;
}

.empty-payments {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

.select-with-search {
  position: relative;
}

.search-input {
  cursor: pointer;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 6px 6px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dropdown-item {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item.no-results {
  color: #7f8c8d;
  cursor: default;
  font-style: italic;
}

.dropdown-item.no-results:hover {
  background: white;
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
  
  .payments-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .payments-grid {
    grid-template-columns: 1fr;
  }
}
</style>