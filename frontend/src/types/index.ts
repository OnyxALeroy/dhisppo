export enum UserRole {
  UNAUTHENTICATED = "unauthenticated",
  USER = "user",
  ORGANIZER = "organizer",
  ADMIN = "admin",
}

export interface User {
  id: string;
  email: string;
  username: string;
  role: UserRole;
  created_at: string;
  is_active: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Participant {
  user_id: string;
  tags: string[];
  due_payment: number;
  paid_amount: number;
}

export interface Event {
  id: string;
  name: string;
  organizers: string[];
  locations: string[];
  description: string;
  start_date: string;
  end_date?: string;
  start_time: string;
  end_time?: string;
  images: string[];
  notes: string[];
  participants: Participant[];
  payments: Payment[];
  expenditures?: Expenditure[];
  created_at: string;
  updated_at?: string;
}

export interface EventCreate {
  name: string;
  organizers: string[];
  locations: string[];
  description: string;
  start_date: string;
  end_date?: string;
  start_time: string;
  end_time?: string;
  images?: string[];
  notes?: string[];
  participants?: Participant[];
  payments?: Payment[];
  expenditures?: Expenditure[];
}

export interface EventUpdate {
  name?: string;
  organizers?: string[];
  locations?: string[];
  description?: string;
  start_date?: string;
  end_date?: string;
  start_time?: string;
  end_time?: string;
  images?: string[];
  notes?: string[];
  participants?: Participant[];
  payments?: Payment[];
  expenditures?: Expenditure[];
}

export interface UserInfo {
  id: string;
  username: string;
  email?: string;
}

export interface Payment {
  id: string;
  sender: UserInfo;
  receiver: UserInfo;
  amount: number;
  title: string;
  created_at: string;
}

export interface PaymentCreate {
  sender: UserInfo;
  receiver: UserInfo;
  amount: number;
  title: string;
}

export interface PaymentUpdate {
  amount?: number;
  title?: string;
}

export interface Expenditure {
  id: string;
  payer_id: string;
  payer: UserInfo;
  amount: number;
  receiver: string;
  description: string;
  created_at: string;
}

export interface ExpenditureCreate {
  payer_id: string;
  amount: number;
  receiver: string;
  description: string;
}

export interface ExpenditureUpdate {
  amount?: number;
  receiver?: string;
  description?: string;
}
