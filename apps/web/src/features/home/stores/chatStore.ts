import { createMessage, type ChatMessage, type ChatState } from "../entities/chat.ts";

type Listener = (state: ChatState) => void;

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
};

let state = initialState;
const listeners = new Set<Listener>();

export const chatStore = {
  reset: (welcome: string) => {
    state = { messages: [createMessage('assistant', welcome)], isLoading: false, error: null };
    listeners.forEach((listener) => listener(state));
  },
  getState: () => state,
  subscribe: (listener: Listener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  addMessage: (message: ChatMessage) => {
    state = { ...state, messages: [...state.messages, message], error: null };
    listeners.forEach((listener) => listener(state));
  },
  setLoading: (isLoading: boolean) => {
    state = { ...state, isLoading };
    listeners.forEach((listener) => listener(state));
  },
  setError: (error: string | null) => {
    state = { ...state, error };
    listeners.forEach((listener) => listener(state));
  },
};
