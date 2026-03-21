import { defineStore } from "pinia";
import { ref } from "vue";
import type { Event, EventCreate, EventUpdate, Participant } from "@/types";
import { eventsAPI } from "@/utils/api";

export const useEventStore = defineStore("events", () => {
  const events = ref<Event[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchEvents = async (organizer?: string, location?: string) => {
    loading.value = true;
    error.value = null;
    try {
      events.value = await eventsAPI.getEvents(organizer, location);
    } catch (err) {
      error.value = "Failed to fetch events";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchEvent = async (id: string) => {
    loading.value = true;
    error.value = null;
    try {
      const event = await eventsAPI.getEvent(id);
      const index = events.value.findIndex((e) => e.id === id);
      if (index !== -1) {
        events.value[index] = event;
      } else {
        events.value.push(event);
      }
      return event;
    } catch (err) {
      error.value = "Failed to fetch event";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const createEvent = async (eventData: EventCreate) => {
    loading.value = true;
    error.value = null;
    try {
      const newEvent = await eventsAPI.createEvent(eventData);
      events.value.push(newEvent);
      return newEvent;
    } catch (err) {
      error.value = "Failed to create event";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateEvent = async (id: string, updateData: EventUpdate) => {
    loading.value = true;
    error.value = null;
    try {
      const updatedEvent = await eventsAPI.updateEvent(id, updateData);
      const index = events.value.findIndex((e) => e.id === id);
      if (index !== -1) {
        events.value[index] = updatedEvent;
      }
      return updatedEvent;
    } catch (err) {
      error.value = "Failed to update event";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deleteEvent = async (id: string) => {
    loading.value = true;
    error.value = null;
    try {
      await eventsAPI.deleteEvent(id);
      events.value = events.value.filter((e) => e.id !== id);
    } catch (err) {
      error.value = "Failed to delete event";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const addParticipant = async (eventId: string, participant: Participant) => {
    loading.value = true;
    error.value = null;
    try {
      const updatedEvent = await eventsAPI.addParticipant(eventId, participant);
      const index = events.value.findIndex((e) => e.id === eventId);
      if (index !== -1) {
        events.value[index] = updatedEvent;
      }
      return updatedEvent;
    } catch (err) {
      error.value = "Failed to add participant";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const removeParticipant = async (eventId: string, userId: string) => {
    loading.value = true;
    error.value = null;
    try {
      const updatedEvent = await eventsAPI.removeParticipant(eventId, userId);
      const index = events.value.findIndex((e) => e.id === eventId);
      if (index !== -1) {
        events.value[index] = updatedEvent;
      }
      return updatedEvent;
    } catch (err) {
      error.value = "Failed to remove participant";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateParticipantPayment = async (
    eventId: string,
    userId: string,
    paidAmount: number,
  ) => {
    loading.value = true;
    error.value = null;
    try {
      const updatedEvent = await eventsAPI.updateParticipantPayment(
        eventId,
        userId,
        paidAmount,
      );
      const index = events.value.findIndex((e) => e.id === eventId);
      if (index !== -1) {
        events.value[index] = updatedEvent;
      }
      return updatedEvent;
    } catch (err) {
      error.value = "Failed to update payment";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const inviteUser = async (eventId: string, userId: string) => {
    loading.value = true;
    error.value = null;
    try {
      await eventsAPI.inviteUser(eventId, userId);
    } catch (err) {
      error.value = "Failed to send invitation";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const acceptInvitation = async (eventId: string) => {
    loading.value = true;
    error.value = null;
    try {
      const updatedEvent = await eventsAPI.acceptInvitation(eventId);
      const index = events.value.findIndex((e) => e.id === eventId);
      if (index !== -1) {
        events.value[index] = updatedEvent;
      } else {
        events.value.push(updatedEvent);
      }
      return updatedEvent;
    } catch (err) {
      error.value = "Failed to accept invitation";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    events,
    loading,
    error,
    fetchEvents,
    fetchEvent,
    createEvent,
    updateEvent,
    deleteEvent,
    addParticipant,
    removeParticipant,
    updateParticipantPayment,
    inviteUser,
    acceptInvitation,
  };
});
