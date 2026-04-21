import { create } from "zustand";

interface UiState {
  pendingRequests: number;
  increasePending: () => void;
  decreasePending: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  pendingRequests: 0,
  increasePending: () =>
    set((state) => ({ pendingRequests: state.pendingRequests + 1 })),
  decreasePending: () =>
    set((state) => ({
      pendingRequests: Math.max(0, state.pendingRequests - 1),
    })),
}));
