import axios from "axios";
import type {
  User,
  LoginRequest,
  RegisterRequest,
  Token,
  Event,
  EventCreate,
  EventUpdate,
  Participant,
  Payment,
  PaymentCreate,
  PaymentUpdate,
} from "@/types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (data: LoginRequest): Promise<Token> =>
    api.post("/auth/login", data).then((res) => res.data),

  register: (data: RegisterRequest): Promise<User> =>
    api.post("/auth/register", data).then((res) => res.data),

  getCurrentUser: (): Promise<User> =>
    api.get("/auth/me").then((res) => res.data),

  getUsers: (): Promise<User[]> =>
    api.get("/auth/users").then((res) => res.data),

  updateUser: (userId: string, data: { email?: string; username?: string; role?: string }): Promise<User> =>
    api.patch(`/auth/users/${userId}`, data).then((res) => res.data),

  deleteUser: (userId: string): Promise<void> =>
    api.delete(`/auth/users/${userId}`).then((res) => res.data),
};

export const eventsAPI = {
  getEvents: (organizer?: string, location?: string): Promise<Event[]> =>
    api
      .get("/events/", { params: { organizer, location } })
      .then((res) => res.data),

  getEvent: (id: string): Promise<Event> =>
    api.get(`/events/${id}`).then((res) => res.data),

  createEvent: (data: EventCreate): Promise<Event> =>
    api.post("/events/", data).then((res) => res.data),

  updateEvent: (id: string, data: EventUpdate): Promise<Event> =>
    api.patch(`/events/${id}`, data).then((res) => res.data),

  deleteEvent: (id: string): Promise<void> =>
    api.delete(`/events/${id}`).then((res) => res.data),

  addParticipant: (eventId: string, participant: Participant): Promise<Event> =>
    api
      .post(`/events/${eventId}/participants`, participant)
      .then((res) => res.data),

  removeParticipant: (eventId: string, userId: string): Promise<Event> =>
    api
      .delete(`/events/${eventId}/participants/${userId}`)
      .then((res) => res.data),

  updateParticipantPayment: (
    eventId: string,
    userId: string,
    paidAmount: number,
  ): Promise<Event> =>
    api
      .patch(`/events/${eventId}/participants/${userId}/payment`, null, {
        params: { paid_amount: paidAmount },
      })
      .then((res) => res.data),
};

export const paymentsAPI = {
  createPayment: (eventId: string, payment: PaymentCreate): Promise<Payment> =>
    api.post(`/payments/events/${eventId}/payments`, payment).then((res) => res.data),

  getEventPayments: (eventId: string): Promise<Payment[]> =>
    api.get(`/payments/events/${eventId}/payments`).then((res) => res.data),

  getPayment: (eventId: string, paymentId: string): Promise<Payment> =>
    api.get(`/payments/events/${eventId}/payments/${paymentId}`).then((res) => res.data),

  updatePayment: (eventId: string, paymentId: string, payment: PaymentUpdate): Promise<Payment> =>
    api.patch(`/payments/events/${eventId}/payments/${paymentId}`, payment).then((res) => res.data),

  deletePayment: (eventId: string, paymentId: string): Promise<void> =>
    api.delete(`/payments/events/${eventId}/payments/${paymentId}`).then((res) => res.data),

  getUserPayments: (userId: string): Promise<Payment[]> =>
    api.get(`/payments/user/${userId}/payments`).then((res) => res.data),

  getMyPayments: (): Promise<Payment[]> =>
    api.get(`/payments/my/payments`).then((res) => res.data),
};

export default api;
