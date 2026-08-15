import { create } from "zustand";

interface UIState {
  selectedSchema: string | null;
  searchQuery: string;
  tableSortBy: "name" | "rows" | "columns";
  tableSortDir: "asc" | "desc";
  activeRunId: string | null;

  // Actions
  setSelectedSchema: (schema: string | null) => void;
  setSearchQuery: (query: string) => void;
  setTableSort: (
    sortBy: "name" | "rows" | "columns",
    sortDir: "asc" | "desc"
  ) => void;
  setActiveRunId: (runId: string | null) => void;
  resetFilters: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  selectedSchema: null,
  searchQuery: "",
  tableSortBy: "name",
  tableSortDir: "asc",
  activeRunId: null,

  setSelectedSchema: (schema) => set({ selectedSchema: schema }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setTableSort: (sortBy, sortDir) =>
    set({ tableSortBy: sortBy, tableSortDir: sortDir }),
  setActiveRunId: (runId) => set({ activeRunId: runId }),
  resetFilters: () =>
    set({
      selectedSchema: null,
      searchQuery: "",
      tableSortBy: "name",
      tableSortDir: "asc",
    }),
}));
