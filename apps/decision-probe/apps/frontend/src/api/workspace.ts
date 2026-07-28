import { Workspace } from '@/store/workspaceStore';

const API_BASE = 'http://localhost:8005/api/v1';

export const workspaceApi = {
  async getWorkspaces(): Promise<Workspace[]> {
    const res = await fetch(`${API_BASE}/workspaces`);
    if (!res.ok) throw new Error('Failed to fetch workspaces');
    return res.json();
  },

  async getWorkspace(id: string): Promise<Workspace> {
    const res = await fetch(`${API_BASE}/workspaces/${id}`);
    if (!res.ok) throw new Error('Failed to fetch workspace');
    return res.json();
  },

  async createWorkspace(title: string): Promise<Workspace> {
    const res = await fetch(`${API_BASE}/workspaces`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, initial_blocks: [] })
    });
    if (!res.ok) throw new Error('Failed to create workspace');
    return res.json();
  },

  async updateWorkspace(id: string, title: string): Promise<Workspace> {
    const res = await fetch(`${API_BASE}/workspaces/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
    if (!res.ok) throw new Error('Failed to update workspace');
    return res.json();
  },

  async deleteWorkspace(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/workspaces/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete workspace');
  },

  async uploadResource(id: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch(`${API_BASE}/workspaces/${id}/resources`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload resource');
    return res.json();
  },

  async uploadDocument(id: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch(`${API_BASE}/workspaces/${id}/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload document');
    return res.json();
  },

  async getDocumentStatus(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/workspaces/${id}/status`);
    if (!res.ok) throw new Error('Failed to fetch document status');
    return res.json();
  },

  async startInvestigation(id: string, goal: string): Promise<any> {
    const res = await fetch(`${API_BASE}/workspaces/${id}/investigate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal })
    });
    if (!res.ok) throw new Error('Failed to start investigation');
    return res.json();
  },

  async getPlan(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/workspaces/${id}/plan`);
    if (!res.ok) throw new Error('Failed to fetch plan');
    return res.json();
  },


  async getProviders(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/workspaces/settings/providers`);
    if (!res.ok) throw new Error('Failed to fetch providers');
    return res.json();
  },

  async updateProvider(id: string, enabled: boolean): Promise<any> {
    const res = await fetch(`${API_BASE}/workspaces/settings/providers/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    if (!res.ok) throw new Error('Failed to update provider');
    return res.json();
  }
};
