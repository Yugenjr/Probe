import { create } from 'zustand';

interface UIState {
  isRightPanelOpen: boolean;
  isLeftSidebarOpen: boolean;
  toggleRightPanel: () => void;
  toggleLeftSidebar: () => void;
  setRightPanelOpen: (isOpen: boolean) => void;
  setLeftSidebarOpen: (isOpen: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  isRightPanelOpen: true,
  isLeftSidebarOpen: true,
  toggleRightPanel: () => set((state) => ({ isRightPanelOpen: !state.isRightPanelOpen })),
  toggleLeftSidebar: () => set((state) => ({ isLeftSidebarOpen: !state.isLeftSidebarOpen })),
  setRightPanelOpen: (isOpen) => set({ isRightPanelOpen: isOpen }),
  setLeftSidebarOpen: (isOpen) => set({ isLeftSidebarOpen: isOpen }),
}));
