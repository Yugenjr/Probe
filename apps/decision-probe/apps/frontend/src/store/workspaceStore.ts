import { create } from 'zustand';

export interface Block {
  id: string;
  type: string;
  order: number;
  content: any;
}

export interface LogEntry {
  id?: string;
  message: string;
  success: boolean;
  timestamp?: string;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Workspace {
  id: string;
  title: string;
  blocks: Block[];
  conversations: ChatMessage[];
  execution_logs: LogEntry[];
  metadata?: any;
}

interface WorkspaceState {
  activeWorkspace: Workspace | null;
  setActiveWorkspace: (workspace: Workspace | null) => void;
  appendBlock: (block: Block) => void;
  updateBlock: (id: string, content: any) => void;
  removeBlock: (id: string) => void;
  applyPatches: (patches: any[]) => void;
  
  // Ephemeral UI State
  isThinking: boolean;
  errorMessage: string;
  
  // Actions
  appendMessage: (msg: ChatMessage) => void;
  appendLog: (log: LogEntry) => void;
  clearExecutionLogs: () => void;
  setIsThinking: (val: boolean) => void;
  setErrorMessage: (msg: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  (set) => ({
    activeWorkspace: null,
    isThinking: false,
    errorMessage: "",
    
    setActiveWorkspace: (workspace) => set({ activeWorkspace: workspace }),
    
    setIsThinking: (val) => set({ isThinking: val }),
    setErrorMessage: (msg) => set({ errorMessage: msg }),
    
    appendMessage: (msg) => set((state) => {
      if (!state.activeWorkspace) return state;
      return {
        activeWorkspace: {
          ...state.activeWorkspace,
          conversations: [...state.activeWorkspace.conversations, msg]
        }
      };
    }),
    
    appendLog: (log) => set((state) => {
      if (!state.activeWorkspace) return state;
      return {
        activeWorkspace: {
          ...state.activeWorkspace,
          execution_logs: [...state.activeWorkspace.execution_logs, log]
        }
      };
    }),
    
    clearExecutionLogs: () => set((state) => {
      if (!state.activeWorkspace) return state;
      return {
        activeWorkspace: {
          ...state.activeWorkspace,
          execution_logs: []
        }
      };
    }),
    
    appendBlock: (block) => set((state) => {
      if (!state.activeWorkspace) return state;
      return {
        activeWorkspace: {
          ...state.activeWorkspace,
          blocks: [...state.activeWorkspace.blocks, block]
        }
      };
    }),

    updateBlock: (id, content) => set((state) => {
      if (!state.activeWorkspace) return state;
      return {
        activeWorkspace: {
          ...state.activeWorkspace,
          blocks: state.activeWorkspace.blocks.map(b => 
            b.id === id ? { ...b, content: { ...b.content, ...content } } : b
          )
        }
      };
    }),

    removeBlock: (id) => set((state) => {
      if (!state.activeWorkspace) return state;
      return {
        activeWorkspace: {
          ...state.activeWorkspace,
          blocks: state.activeWorkspace.blocks.filter(b => b.id !== id)
        }
      };
    }),

    applyPatches: (patches) => set((state) => {
      if (!state.activeWorkspace) return state;
      
      let newBlocks = [...state.activeWorkspace.blocks];
      
      patches.forEach(patchGroup => {
        if (patchGroup.type === 'PatchOperation') {
          patchGroup.operations.forEach((op: any) => {
            if (op.op === 'append_block' || op.op.startsWith('append_')) {
              if (!op.payload?.id) {
                console.error("Patch operation missing block ID. Rejected.", op);
                return;
              }

              const type = op.op.startsWith('append_') && op.op !== 'append_block' 
                ? op.op.split('_')[1] 
                : op.payload?.type;
                
              newBlocks.push({
                id: op.payload.id,
                type: type || 'text',
                order: op.payload?.order ?? newBlocks.length,
                content: op.payload?.content || op.payload || {}
              });
            } else if (op.op === 'update_block') {
              newBlocks = newBlocks.map(b => b.id === op.target_id ? { ...b, content: { ...b.content, ...op.payload?.content } } : b);
            } else if (op.op === 'replace_block') {
              newBlocks = newBlocks.map(b => b.id === op.target_id ? { ...b, content: op.payload?.content || op.payload } : b);
            } else if (op.op === 'delete_block') {
              newBlocks = newBlocks.filter(b => b.id !== op.target_id);
            }
          });
        }
      });

      newBlocks.sort((a, b) => a.order - b.order);

      return {
        activeWorkspace: {
          ...state.activeWorkspace,
          blocks: newBlocks
        }
      };
    })
  })
);
