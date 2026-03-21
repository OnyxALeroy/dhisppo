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
          <div class="participant-actions">
            <button 
              v-if="canInviteUsers"
              class="btn-secondary"
              @click="showInviteUser = true"
            >
              Invite User
            </button>
            <button 
              class="btn-primary"
              @click="showAddParticipant = true"
            >
              Add Participant
            </button>
          </div>
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
              <div class="participant-info">
                <h4>{{ getUserDisplay(participant.user_id).split(' (')[0] }}</h4>
                <p class="participant-email">{{ getUserEmail(participant.user_id) }}</p>
                <p class="participant-address" v-if="getUserAddress(participant.user_id)">
                  📍 {{ getUserAddress(participant.user_id) }}
                </p>
              </div>
              <button 
                class="btn-danger btn-small"
                @click="removeParticipant(participant.user_id)"
              >
                Remove
              </button>
            </div>
            
            <div class="participant-stats">
              <div class="stat-item">
                <span class="stat-label">Due</span>
                <span class="stat-value due">${{ perPersonDue.toFixed(2) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Paid</span>
                <span class="stat-value paid">${{ participant.paid_amount.toFixed(2) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Balance</span>
                <span class="stat-value" :class="perPersonDue - participant.paid_amount <= 0 ? 'paid' : 'due'">
                  ${{ (perPersonDue - participant.paid_amount).toFixed(2) }}
                </span>
              </div>
            </div>
            
            <div class="participant-history">
              <button 
                class="history-toggle"
                @click="toggleParticipantPayments(participant.user_id)"
              >
                {{ expandedParticipantId === participant.user_id ? '▼' : '▶' }} 
                Payment History ({{ getParticipantPayments(participant.user_id).length }})
              </button>
              
              <div v-if="expandedParticipantId === participant.user_id" class="history-list">
                <table class="history-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Amount</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="payment in getParticipantPayments(participant.user_id)" :key="payment.id">
                      <td>{{ formatDate(payment.created_at) }}</td>
                      <td class="amount">${{ payment.amount.toFixed(2) }}</td>
                      <td class="actions">
                        <button class="btn-icon" @click="openEditParticipantPayment(payment, participant)" title="Edit">✏️</button>
                        <button class="btn-icon" @click="deleteParticipantPayment(payment.id, participant)" title="Delete">🗑️</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <button class="btn-primary btn-small btn-full" @click="openPaymentModal(participant)">
                  + Add Payment
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Payment History Section -->
      <div class="payment-history-section">
        <div class="payment-history-header">
          <h3>💳 Payment History</h3>
          <div class="payment-history-filters">
            <select v-model="selectedHistoryParticipant" class="form-input">
              <option value="">All Participants</option>
              <option 
                v-for="participant in event.participants" 
                :key="participant.user_id" 
                :value="participant.user_id"
              >
                {{ getUsername(participant.user_id) }}
              </option>
            </select>
            <div class="payment-total">
              Total: <strong>${{ filteredPaymentsTotal.toFixed(2) }}</strong>
            </div>
          </div>
          <button 
            class="btn-primary"
            @click="showAddPayment = true"
          >
            Add Payment
          </button>
        </div>

        <div v-if="filteredPayments.length === 0" class="empty-payments">
          <p>No payment history yet</p>
        </div>

        <div v-else class="payment-history-table">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Title</th>
                <th>From</th>
                <th>To</th>
                <th>Amount</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="payment in filteredPayments" :key="payment.id">
                <td>{{ formatDate(payment.created_at) }}</td>
                <td>{{ payment.title }}</td>
                <td>{{ payment.sender.username }}</td>
                <td>{{ payment.receiver.username }}</td>
                <td class="amount">${{ payment.amount.toFixed(2) }}</td>
                <td>
                  <button class="btn-icon" @click="openEditPaymentModal(payment)" title="Edit">✏️</button>
                  <button class="btn-icon" @click="deletePaymentFromHistory(payment.id)" title="Delete">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Expenditures Section (always visible) -->
      <div class="expenditures-section">
        <div class="expenditures-header">
          <h3>🛒 Expenditures ({{ (event.expenditures || []).length }})</h3>
          <div class="expenditure-summary">
            <span>Total: <strong>${{ totalExpenditures.toFixed(2) }}</strong></span>
            <span class="split-info">(Split {{ allParticipantsCount }} ways: <strong>${{ perPersonDue.toFixed(2) }}</strong>/person)</span>
          </div>
          <button 
            class="btn-primary"
            @click="showAddExpenditure = true"
          >
            Add Expenditure
          </button>
        </div>

        <div v-if="!event.expenditures || event.expenditures.length === 0" class="empty-expenditures">
          <p>No expenditures yet</p>
        </div>

        <div v-else class="expenditures-grid">
          <div 
            v-for="expenditure in event.expenditures" 
            :key="expenditure.id"
            class="expenditure-card"
          >
            <div class="expenditure-header">
              <h4>{{ expenditure.description }}</h4>
              <button 
                class="btn-danger btn-small"
                @click="confirmDeleteExpenditure(expenditure)"
              >
                Delete
              </button>
            </div>
            
            <div class="expenditure-body">
              <div class="expenditure-amount">
                <span class="amount-label">Amount:</span>
                <span class="amount-value">${{ expenditure.amount.toFixed(2) }}</span>
              </div>
              
              <div class="expenditure-participants">
                <div class="expenditure-participant">
                  <span class="participant-label">Paid by:</span>
                  <span class="participant-name">{{ getPayerUsername(expenditure.payer_id, expenditure.payer) }}</span>
                </div>
                <div class="expenditure-participant">
                  <span class="participant-label">Paid to:</span>
                  <span class="participant-name">{{ expenditure.receiver }}</span>
                </div>
              </div>
              
              <div class="expenditure-type">
                <span class="type-label">Type:</span>
                <span class="type-value" :class="'type-' + (expenditure.type || 'other')">{{ capitalizeFirst(expenditure.type || 'other') }}</span>
              </div>
              
              <div class="expenditure-date">
                <span class="date-label">Date:</span>
                <span class="date-value">{{ formatDate(expenditure.created_at) }}</span>
              </div>
              
              <button 
                class="btn-secondary btn-small btn-full"
                @click="openEditExpenditureModal(expenditure)"
              >
                Edit Expenditure
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
              class="form-input"
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeAddParticipant">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="saving || !selectedUserForAdd">
              {{ saving ? 'Adding...' : 'Add Participant' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Invite User Modal -->
    <div v-if="showInviteUser" class="modal-overlay" @click="closeInviteUser">
      <div class="modal" @click.stop>
        <h3>Invite User to Event</h3>
        <p class="modal-subtitle">Search for a user to invite to this private event</p>
        <form @submit.prevent="inviteUser">
          <div class="form-group">
            <label for="inviteUserSearch">Search User</label>
            <div class="select-with-search">
              <input 
                id="inviteUserSearch"
                v-model="inviteSearch" 
                type="text" 
                placeholder="Search by username or email..."
                class="form-input search-input"
                @focus="showInviteDropdown = true"
              />
              <div v-if="showInviteDropdown && (filteredInviteUsers.length > 0 || inviteSearch)" class="dropdown">
                <div 
                  v-for="user in filteredInviteUsers" 
                  :key="user.id"
                  class="dropdown-item"
                  @click="selectInviteUser(user)"
                >
                  {{ user.username }} ({{ user.email }})
                </div>
                <div v-if="filteredInviteUsers.length === 0 && inviteSearch" class="dropdown-item no-results">
                  No users found
                </div>
              </div>
            </div>
          </div>

          <div v-if="selectedInviteUser" class="selected-user-display">
            <span>Selected: </span>
            <strong>{{ selectedInviteUser.username }}</strong>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeInviteUser">
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn-primary" 
              :disabled="saving || !selectedInviteUser"
            >
              {{ saving ? 'Sending...' : 'Send Invitation' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Payment Update Modal -->
    <div v-if="showPaymentModal" class="modal-overlay" @click="closePaymentModal">
      <div class="modal" @click.stop>
        <h3>Update Payment</h3>
        <p>Participant: {{ getUserDisplay(selectedParticipant?.user_id || '') }}</p>
        
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
              v-model.number="paymentCreateForm.amount" 
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
              v-model="paymentCreateForm.title" 
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

    <!-- Add Expenditure Modal -->
    <div v-if="showAddExpenditure" class="modal-overlay" @click="closeAddExpenditure">
      <div class="modal" @click.stop>
        <h3>Add Expenditure</h3>
        <form @submit.prevent="addExpenditure">
          <div class="form-group">
            <label for="expenditurePayer">Paid by</label>
            <div class="select-with-search">
              <input 
                id="expenditurePayer"
                v-model="payerSearch" 
                type="text" 
                placeholder="Search payer..."
                class="form-input search-input"
                @focus="showPayerDropdown = true"
              />
              <div v-if="showPayerDropdown && (filteredPayers.length > 0 || payerSearch)" class="dropdown">
                <div 
                  v-for="user in filteredPayers" 
                  :key="user.id"
                  class="dropdown-item"
                  @click="selectPayer(user)"
                >
                  {{ user.username }}
                </div>
                <div v-if="filteredPayers.length === 0 && payerSearch" class="dropdown-item no-results">
                  No users found
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label for="expenditureReceiver">Paid to</label>
            <input 
              id="expenditureReceiver"
              v-model="expenditureCreateForm.receiver" 
              type="text" 
              required
              class="form-input"
              placeholder="Vendor, service, etc."
            />
          </div>

          <div class="form-group">
            <label for="expenditureAmount">Amount</label>
            <input 
              id="expenditureAmount"
              v-model.number="expenditureCreateForm.amount" 
              type="number" 
              step="0.01"
              min="0"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="expenditureDescription">Description</label>
            <input 
              id="expenditureDescription"
              v-model="expenditureCreateForm.description" 
              type="text" 
              required
              class="form-input"
              placeholder="What was this expenditure for?"
            />
          </div>

          <div class="form-group">
            <label for="expenditureType">Type</label>
            <select 
              id="expenditureType"
              v-model="expenditureCreateForm.type" 
              required
              class="form-input"
            >
              <option value="location">Location</option>
              <option value="food">Food</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeAddExpenditure">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Adding...' : 'Add Expenditure' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Expenditure Modal -->
    <div v-if="showEditExpenditure" class="modal-overlay" @click="closeEditExpenditure">
      <div class="modal" @click.stop>
        <h3>Edit Expenditure</h3>
        <p>Original: {{ selectedExpenditure?.description }}</p>
        
        <form @submit.prevent="editExpenditure">
          <div class="form-group">
            <label for="editExpenditureAmount">Amount</label>
            <input 
              id="editExpenditureAmount"
              v-model.number="editExpenditureForm.amount" 
              type="number" 
              step="0.01"
              min="0"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="editExpenditureReceiver">Paid to</label>
            <input 
              id="editExpenditureReceiver"
              v-model="editExpenditureForm.receiver" 
              type="text" 
              required
              class="form-input"
              placeholder="Vendor, service, etc."
            />
          </div>

          <div class="form-group">
            <label for="editExpenditureDescription">Description</label>
            <input 
              id="editExpenditureDescription"
              v-model="editExpenditureForm.description" 
              type="text" 
              required
              class="form-input"
              placeholder="What was this expenditure for?"
            />
          </div>

          <div class="form-group">
            <label for="editExpenditureType">Type</label>
            <select 
              id="editExpenditureType"
              v-model="editExpenditureForm.type" 
              required
              class="form-input"
            >
              <option value="location">Location</option>
              <option value="food">Food</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeEditExpenditure">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Updating...' : 'Update Expenditure' }}
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
import { eventsAPI, paymentsAPI, expendituresAPI, authAPI, notificationsAPI } from '@/utils/api';
import { useAuthStore } from '@/stores/auth';
import type { Event, Participant, Payment, UserInfo, Expenditure, ExpenditureType } from '@/types';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const event = ref<Event | null>(null);
const loading = ref(true);
const saving = ref(false);
const error = ref<string | null>(null);
const payments = ref<Payment[]>([]);

const expandedParticipantId = ref<string | null>(null);
const selectedHistoryParticipant = ref<string>('');
const selectedPayment = ref<Payment | null>(null);

const isEditMode = ref(false);
const showAddParticipant = ref(false);
const showInviteUser = ref(false);
const showPaymentModal = ref(false);
const showAddPayment = ref(false);
const showEditPayment = ref(false);
const showAddExpenditure = ref(false);
const showEditExpenditure = ref(false);
const selectedImage = ref<string | null>(null);
const availableUsers = ref<UserInfo[]>([]);

const inviteSearch = ref('');
const selectedInviteUser = ref<UserInfo | null>(null);
const showInviteDropdown = ref(false);

const userSearch = ref('');
const selectedUserForAdd = ref<UserInfo | null>(null);
const showUserDropdown = ref(false);

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

const editPaymentForm = reactive({
  amount: 0,
  title: ''
});

const expenditureCreateForm = reactive({
  payer_id: '',
  amount: 0,
  receiver: '',
  description: '',
  type: 'other' as ExpenditureType
});

const selectedExpenditure = ref<Expenditure | null>(null);
const editExpenditureForm = reactive({
  amount: 0,
  receiver: '',
  description: '',
  type: 'other' as ExpenditureType
});

const payerSearch = ref('');
const showPayerDropdown = ref(false);

const loadEvent = async () => {
  try {
    loading.value = true;
    const eventId = route.params.id as string;
    const eventData = await eventsAPI.getEvent(eventId);
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
    
    // Fetch expenditures directly to ensure they're loaded
    try {
      const expendituresData = await expendituresAPI.getEventExpenditures(eventId);
      eventData.expenditures = expendituresData;
    } catch (expenditureErr) {
      console.warn('Failed to load expenditures, using empty array:', expenditureErr);
      eventData.expenditures = [];
    }
    
    event.value = eventData;
    
    // Fetch payments from separate collection
    try {
      const paymentsData = await paymentsAPI.getEventPayments(eventId);
      payments.value = paymentsData;
    } catch (paymentErr) {
      console.warn('Failed to load payments:', paymentErr);
      payments.value = [];
    }
    
    await loadAvailableUsers();
    resetForm();
  } catch (err) {
    error.value = 'Failed to load event';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const sendPaymentNotification = async (userId: string, message: string) => {
  if (!authStore.user || userId === authStore.user.id) return;
  try {
    await notificationsAPI.createNotification({
      sender_id: authStore.user.id,
      receiver_id: userId,
      content: message
    });
  } catch (err) {
    console.error('Failed to send notification:', err);
  }
};

const loadAvailableUsers = async () => {
  try {
    const users = await authAPI.getUsers();
    availableUsers.value = users.map(user => ({
      id: user.id,
      username: user.username,
      email: user.email,
      address: user.address
    }));
  } catch (err) {
    console.error('Failed to load users:', err);
  }
};

const getUsername = (userId: string): string => {
  const user = availableUsers.value.find(u => u.id === userId);
  return user ? user.username : userId;
};

const getUserEmail = (userId: string): string => {
  const user = availableUsers.value.find(u => u.id === userId);
  return user ? user.email : '';
};

const getUserAddress = (userId: string): string => {
  const user = availableUsers.value.find(u => u.id === userId);
  return user?.address || '';
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

const capitalizeFirst = (str: string) => {
  if (!str) return 'Other';
  return str.charAt(0).toUpperCase() + str.slice(1);
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

const getUserDisplay = (userId: string) => {
  const user = availableUsers.value.find(u => u.id === userId);
  if (user) {
    return `${user.username} (${user.email})`;
  }
  return userId;
};

const addParticipant = async () => {
  if (!event.value || !selectedUserForAdd.value) return;
  
  try {
    saving.value = true;
    
    participantForm.user_id = selectedUserForAdd.value.id;

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
  if (!event.value || !selectedParticipant.value || !authStore.user) return;
  
  try {
    saving.value = true;
    
    const oldPaidAmount = selectedParticipant.value.paid_amount;
    const newPaidAmount = paymentForm.paid_amount;
    const participantUser = availableUsers.value.find(u => u.id === selectedParticipant.value.user_id);
    
    await eventsAPI.updateParticipantPayment(
      event.value.id,
      selectedParticipant.value.user_id,
      newPaidAmount
    );
    
    if (newPaidAmount > oldPaidAmount) {
      const paymentAmount = newPaidAmount - oldPaidAmount;
      const receiverUser = availableUsers.value.find(u => u.id === authStore.user?.id) || availableUsers.value[0];
      
      const paymentData = {
        sender: {
          id: selectedParticipant.value.user_id,
          username: participantUser?.username || 'Unknown'
        },
        receiver: {
          id: receiverUser?.id || authStore.user?.id,
          username: receiverUser?.username || authStore.user?.username
        },
        amount: paymentAmount,
        title: `Payment from ${participantUser?.username || 'Unknown'}`
      };
      await paymentsAPI.createPayment(event.value.id, paymentData);
      await sendPaymentNotification(
        selectedParticipant.value.user_id,
        `Your payment for "${event.value.name}" has been updated to $${newPaidAmount.toFixed(2)}`
      );
    }
    
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
    
    payments.value = await paymentsAPI.getEventPayments(event.value.id);
    
    closePaymentModal();
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to update payment';
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
  userSearch.value = '';
  selectedUserForAdd.value = null;
  showUserDropdown.value = false;
};

const closePaymentModal = () => {
  showPaymentModal.value = false;
  selectedParticipant.value = null;
  paymentForm.paid_amount = 0;
};

const toggleParticipantPayments = (userId: string) => {
  if (expandedParticipantId.value === userId) {
    expandedParticipantId.value = null;
  } else {
    expandedParticipantId.value = userId;
  }
};

const getParticipantPayments = (userId: string) => {
  return payments.value.filter(p => 
    p.sender.id === userId || p.receiver.id === userId
  );
};

const openEditParticipantPayment = (payment: Payment, participant: Participant) => {
  selectedPayment.value = payment;
  editPaymentForm.amount = payment.amount;
  editPaymentForm.title = payment.title;
  selectedParticipant.value = participant;
  showEditPayment.value = true;
};

const deleteParticipantPayment = async (paymentId: string, participant: Participant) => {
  if (!event.value) return;
  if (!confirm('Are you sure you want to delete this payment?')) return;
  
  const paymentToDelete = payments.value.find(p => p.id === paymentId);
  
  try {
    saving.value = true;
    await paymentsAPI.deletePayment(event.value.id, paymentId);
    
    if (paymentToDelete) {
      await sendPaymentNotification(
        paymentToDelete.sender.id,
        `A payment of $${paymentToDelete.amount.toFixed(2)} for "${event.value.name}" was deleted`
      );
    }
    
    payments.value = await paymentsAPI.getEventPayments(event.value.id);
  } catch (err) {
    error.value = 'Failed to delete payment';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const deletePaymentFromHistory = async (paymentId: string) => {
  if (!event.value) return;
  if (!confirm('Are you sure you want to delete this payment?')) return;
  
  const paymentToDelete = payments.value.find(p => p.id === paymentId);
  
  try {
    saving.value = true;
    await paymentsAPI.deletePayment(event.value.id, paymentId);
    
    if (paymentToDelete) {
      await sendPaymentNotification(
        paymentToDelete.sender.id,
        `A payment of $${paymentToDelete.amount.toFixed(2)} for "${event.value.name}" was deleted`
      );
    }
    
    payments.value = await paymentsAPI.getEventPayments(event.value.id);
  } catch (err) {
    error.value = 'Failed to delete payment';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const openImageModal = (image: string) => {
  selectedImage.value = image;
};

const closeImageModal = () => {
  selectedImage.value = null;
};

const addPayment = async () => {
  if (!event.value) {
    error.value = 'Event not loaded';
    return;
  }
  if (!paymentCreateForm.sender || !paymentCreateForm.receiver) {
    error.value = 'Please select both sender and receiver';
    return;
  }
  if (paymentCreateForm.amount <= 0) {
    error.value = 'Please enter a valid amount';
    return;
  }
  
  try {
    saving.value = true;
    error.value = null;
    
    await paymentsAPI.createPayment(event.value.id, {
      sender: paymentCreateForm.sender,
      receiver: paymentCreateForm.receiver,
      amount: paymentCreateForm.amount,
      title: paymentCreateForm.title
    });
    
    await sendPaymentNotification(
      paymentCreateForm.sender.id,
      `A new payment of $${paymentCreateForm.amount.toFixed(2)} was recorded for "${event.value.name}"`
    );
    
    payments.value = await paymentsAPI.getEventPayments(event.value.id);
    
    closeAddPayment();
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to add payment';
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
    
    await sendPaymentNotification(
      selectedPayment.value.sender.id,
      `Your payment for "${event.value.name}" was updated to $${editPaymentForm.amount.toFixed(2)}`
    );
    
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
    
    payments.value = await paymentsAPI.getEventPayments(event.value.id);
    
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
  
  const paymentToDelete = payments.value.find(p => p.id === paymentId);
  
  try {
    saving.value = true;
    
    await paymentsAPI.deletePayment(event.value.id, paymentId);
    
    if (paymentToDelete) {
      await sendPaymentNotification(
        paymentToDelete.sender.id,
        `A payment of $${paymentToDelete.amount.toFixed(2)} for "${event.value.name}" was deleted`
      );
    }
    
    const updatedEvent = await eventsAPI.getEvent(event.value.id);
    event.value = updatedEvent;
    
    payments.value = await paymentsAPI.getEventPayments(event.value.id);
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

const addExpenditure = async () => {
  if (!event.value || !expenditureCreateForm.payer_id) return;
  
  try {
    saving.value = true;
    
    await expendituresAPI.createExpenditure(event.value.id, {
      payer_id: expenditureCreateForm.payer_id,
      amount: expenditureCreateForm.amount,
      receiver: expenditureCreateForm.receiver,
      description: expenditureCreateForm.description,
      type: expenditureCreateForm.type
    });
    
    // Fetch the updated expenditures directly
    const updatedExpenditures = await expendituresAPI.getEventExpenditures(event.value.id);
    if (event.value) {
      event.value.expenditures = updatedExpenditures;
    }
    
    closeAddExpenditure();
  } catch (err) {
    error.value = 'Failed to add expenditure';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const openEditExpenditureModal = (expenditure: Expenditure) => {
  selectedExpenditure.value = expenditure;
  editExpenditureForm.amount = expenditure.amount;
  editExpenditureForm.receiver = expenditure.receiver;
  editExpenditureForm.description = expenditure.description;
  editExpenditureForm.type = expenditure.type;
  showEditExpenditure.value = true;
};

const editExpenditure = async () => {
  if (!event.value || !selectedExpenditure.value) return;
  
  try {
    saving.value = true;
    
    await expendituresAPI.updateExpenditure(event.value.id, selectedExpenditure.value.id, {
      amount: editExpenditureForm.amount,
      receiver: editExpenditureForm.receiver,
      description: editExpenditureForm.description,
      type: editExpenditureForm.type
    });
    
    // Fetch the updated expenditures directly
    const updatedExpenditures = await expendituresAPI.getEventExpenditures(event.value.id);
    if (event.value) {
      event.value.expenditures = updatedExpenditures;
    }
    
    closeEditExpenditure();
  } catch (err) {
    error.value = 'Failed to update expenditure';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const confirmDeleteExpenditure = (expenditure: Expenditure) => {
  if (!event.value) return;
  if (confirm(`Are you sure you want to delete this expenditure: "${expenditure.description}"?`)) {
    deleteExpenditure(expenditure.id);
  }
};

const deleteExpenditure = async (expenditureId: string) => {
  if (!event.value) return;
  
  try {
    saving.value = true;
    
    await expendituresAPI.deleteExpenditure(event.value.id, expenditureId);
    
    // Fetch the updated expenditures directly
    const updatedExpenditures = await expendituresAPI.getEventExpenditures(event.value.id);
    if (event.value) {
      event.value.expenditures = updatedExpenditures;
    }
  } catch (err) {
    error.value = 'Failed to delete expenditure';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const closeAddExpenditure = () => {
  showAddExpenditure.value = false;
  Object.assign(expenditureCreateForm, {
    payer_id: '',
    amount: 0,
    receiver: '',
    description: '',
    type: 'other' as ExpenditureType
  });
  payerSearch.value = '';
  showPayerDropdown.value = false;
};

const closeEditExpenditure = () => {
  showEditExpenditure.value = false;
  selectedExpenditure.value = null;
  Object.assign(editExpenditureForm, {
    amount: 0,
    receiver: '',
    description: '',
    type: 'other' as ExpenditureType
  });
};

const totalPayments = computed(() => {
  return payments.value.reduce((sum, payment) => sum + payment.amount, 0);
});

const filteredPayments = computed(() => {
  if (!selectedHistoryParticipant.value) {
    return payments.value;
  }
  return payments.value.filter(p => 
    p.sender.id === selectedHistoryParticipant.value || 
    p.receiver.id === selectedHistoryParticipant.value
  );
});

const filteredPaymentsTotal = computed(() => {
  return filteredPayments.value.reduce((sum, payment) => sum + payment.amount, 0);
});

const totalExpenditures = computed(() => {
  if (!event.value?.expenditures) return 0;
  return event.value.expenditures.reduce((sum, exp) => sum + exp.amount, 0);
});

const allParticipantsCount = computed(() => {
  if (!event.value) return 0;
  const participantCount = event.value.participants?.length || 0;
  const organizerCount = event.value.organizers?.length || 0;
  const uniqueOrganizers = event.value.organizers?.filter(org => 
    !event.value?.participants?.some(p => p.user_id === org)
  ).length || 0;
  return participantCount + uniqueOrganizers;
});

const perPersonDue = computed(() => {
  if (allParticipantsCount.value === 0) return 0;
  return totalExpenditures.value / allParticipantsCount.value;
});

const canInviteUsers = computed(() => {
  if (!event.value || !authStore.user) return false;
  if (authStore.isAdmin) return true;
  if (event.value.organizers.includes(authStore.user.username)) {
    return true;
  }
  return false;
});

const filteredInviteUsers = computed(() => {
  const currentUserId = authStore.user?.id;
  const participantUserIds = new Set(event.value?.participants.map(p => p.user_id) || []);
  
  // Filter out current user and existing participants
  let availableForInvite = availableUsers.value.filter(user => {
    const isCurrentUser = user.id === currentUserId;
    const isParticipant = participantUserIds.has(user.id);
    return !isCurrentUser && !isParticipant;
  });
  
  // If search is empty, return all available
  if (!inviteSearch.value.trim()) {
    return availableForInvite;
  }
  
  // Filter by search term
  const searchLower = inviteSearch.value.toLowerCase().trim();
  return availableForInvite.filter(user => 
    user.username.toLowerCase().includes(searchLower) ||
    (user.email && user.email.toLowerCase().includes(searchLower))
  );
});

const filteredUsersForAdd = computed(() => {
  const currentUserId = authStore.user?.id;
  const participantUserIds = new Set(event.value?.participants.map(p => p.user_id) || []);
  
  let available = availableUsers.value.filter(user => {
    const isCurrentUser = user.id === currentUserId;
    const isParticipant = participantUserIds.has(user.id);
    return !isCurrentUser && !isParticipant;
  });
  
  if (!userSearch.value.trim()) {
    return available;
  }
  
  const searchLower = userSearch.value.toLowerCase().trim();
  return available.filter(user => 
    user.username.toLowerCase().includes(searchLower) ||
    (user.email && user.email.toLowerCase().includes(searchLower))
  );
});

const selectUserForAdd = (user: UserInfo) => {
  selectedUserForAdd.value = user;
  userSearch.value = user.username;
  showUserDropdown.value = false;
};

const selectInviteUser = (user: UserInfo) => {
  selectedInviteUser.value = user;
  inviteSearch.value = user.username;
  showInviteDropdown.value = false;
};

const inviteUser = async () => {
  if (!event.value || !selectedInviteUser.value) return;
  
  try {
    saving.value = true;
    await eventsAPI.inviteUser(event.value.id, selectedInviteUser.value.id);
    closeInviteUser();
  } catch (err) {
    error.value = 'Failed to send invitation';
    console.error(err);
  } finally {
    saving.value = false;
  }
};

const closeInviteUser = () => {
  showInviteUser.value = false;
  inviteSearch.value = '';
  selectedInviteUser.value = null;
  showInviteDropdown.value = false;
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

const filteredPayers = computed(() => {
  if (!payerSearch.value) return availableUsers.value;
  return availableUsers.value.filter(user => 
    user.username.toLowerCase().includes(payerSearch.value.toLowerCase()) ||
    user.email.toLowerCase().includes(payerSearch.value.toLowerCase())
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

const getPayerUsername = (payerId: string, payer?: UserInfo) => {
  // If payer info is available, use it directly
  if (payer) {
    return payer.username;
  }
  // Otherwise, look up from available users
  const user = availableUsers.value.find(u => u.id === payerId);
  return user ? user.username : payerId;
};

const selectPayer = (user: UserInfo) => {
  expenditureCreateForm.payer_id = user.id;
  payerSearch.value = user.username;
  showPayerDropdown.value = false;
};

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest('.select-with-search')) {
    showSenderDropdown.value = false;
    showReceiverDropdown.value = false;
    showPayerDropdown.value = false;
    showInviteDropdown.value = false;
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

.participant-actions {
  display: flex;
  gap: 0.5rem;
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
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e8e8;
  overflow: hidden;
}

.participant-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.25rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.participant-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.participant-email {
  font-size: 0.875rem;
  opacity: 0.9;
  margin: 0;
}

.participant-address {
  font-size: 0.8rem;
  opacity: 0.8;
  margin: 0.25rem 0 0 0;
}

.participant-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  border-bottom: 1px solid #e8e8e8;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  text-align: center;
  border-right: 1px solid #e8e8e8;
}

.stat-item:last-child {
  border-right: none;
}

.stat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #888;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
}

.stat-value.due {
  color: #e74c3c;
}

.stat-value.paid {
  color: #27ae60;
}

.participant-history {
  padding: 0;
}

.history-toggle {
  width: 100%;
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  border-bottom: 1px solid #e8e8e8;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.history-toggle:hover {
  background: #f8f9fa;
}

.history-list {
  padding: 1rem;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.history-table th {
  text-align: left;
  padding: 0.5rem;
  color: #888;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  border-bottom: 1px solid #e8e8e8;
}

.history-table td {
  padding: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.history-table td.amount {
  font-weight: 600;
  color: #27ae60;
}

.history-table td.actions {
  text-align: right;
}

.btn-full {
  width: 100%;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  cursor: pointer;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
  border: none;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-danger {
  background: #e74c3c;
  color: white;
  border: none;
  cursor: pointer;
}

.btn-danger:hover {
  background: #c0392b;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1rem;
}

.btn-icon:hover {
  opacity: 0.6;
}

.payment-history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.payment-history-header h3 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.3rem;
}

.payment-total {
  background: #27ae60;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 1rem;
}

.payment-total strong {
  font-size: 1.2rem;
}

.payment-history-table {
  overflow-x: auto;
}

.payment-history-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.payment-history-table th,
.payment-history-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #ecf0f1;
}

.payment-history-table th {
  background: #e8f4fc;
  font-weight: 600;
  color: #2c3e50;
}

.payment-history-table td {
  color: #555;
}

.payment-history-table td.amount {
  font-weight: 600;
  color: #27ae60;
}

.payment-history-table tbody tr:hover {
  background: #f8f9fa;
}

.expenditures-section {
  background: #fef8e7;
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #f0e68c;
  margin-top: 2rem;
}

.expenditures-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.expenditure-summary {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  color: #856404;
  background: #fff3cd;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.expenditure-summary strong {
  font-size: 1.1rem;
}

.split-info {
  font-size: 0.85rem;
  color: #666;
}

.expenditures-section h3 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.3rem;
}

.expenditures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 1rem;
}

.expenditure-card {
  background: white;
  padding: 1.2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0e68c;
}

.expenditure-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.expenditure-header h4 {
  color: #2c3e50;
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.expenditure-body {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.expenditure-amount {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #fff3cd;
  border-radius: 6px;
}

.expenditure-amount .amount-label {
  font-weight: 500;
  color: #856404;
}

.expenditure-amount .amount-value {
  font-weight: 700;
  color: #856404;
  font-size: 1.1rem;
}

.expenditure-participants {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.expenditure-participant {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expenditure-type {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.type-label {
  font-weight: 500;
  color: #666;
}

.type-value {
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.type-location {
  background: #e3f2fd;
  color: #1976d2;
}

.type-food {
  background: #fff3e0;
  color: #f57c00;
}

.type-other {
  background: #f3e5f5;
  color: #7b1fa2;
}

.expenditure-date {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #666;
}

.empty-expenditures {
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
  
  .expenditures-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .expenditures-grid {
    grid-template-columns: 1fr;
  }
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
  z-index: 9999;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal h3 {
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.modal-subtitle {
  color: #666;
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  justify-content: flex-end;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.image-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.image-modal {
  max-width: 90vw;
  max-height: 90vh;
  position: relative;
}

.modal-image {
  max-width: 100%;
  max-height: 90vh;
  border-radius: 8px;
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

.close-image:hover {
  opacity: 0.8;
}

</style>