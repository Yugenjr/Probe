"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { workspaceApi } from '@/api/workspace';

export interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [providers, setProviders] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadProviders();
    }
  }, [isOpen]);

  const loadProviders = async () => {
    setLoading(true);
    try {
      const data = await workspaceApi.getProviders();
      setProviders(data);
    } catch (e) {
      console.error("Failed to load providers", e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const toggleProvider = async (id: string, currentEnabled: boolean) => {
    try {
      // Optimistic update
      setProviders(providers.map(p => p.id === id ? { ...p, enabled: !currentEnabled } : p));
      await workspaceApi.updateProvider(id, !currentEnabled);
    } catch (e) {
      console.error("Failed to update provider", e);
      // Revert on error
      setProviders(providers.map(p => p.id === id ? { ...p, enabled: currentEnabled } : p));
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white w-full max-w-lg rounded-xl shadow-2xl overflow-hidden"
        >
          <div className="flex items-center justify-between p-4 border-b border-neutral-200">
            <h2 className="text-lg font-bold text-neutral-800 flex items-center gap-2">
              API Settings
              {loading && <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />}
            </h2>
            <button onClick={onClose} className="p-1 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-md">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="p-6">
            <p className="text-sm text-neutral-500 mb-6">
              Configure your inference providers. The engine will automatically failover to the next enabled provider if one fails.
            </p>
            
            <div className="space-y-4">
              {providers.map(provider => (
                <div key={provider.id} className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
                  <div className="flex items-center gap-3">
                    <input 
                      type="checkbox" 
                      checked={provider.enabled}
                      onChange={() => toggleProvider(provider.id, provider.enabled)}
                      className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                    />
                    <div>
                      <h4 className="font-semibold text-neutral-800">{provider.name}</h4>
                      <div className="flex items-center gap-1 mt-1 text-xs text-neutral-500">
                        Status: 
                        {provider.status === 'healthy' ? <CheckCircle className="w-3 h-3 text-green-500" /> : <AlertCircle className="w-3 h-3 text-yellow-500" />}
                        <span className={provider.status === 'healthy' ? 'text-green-600' : 'text-yellow-600'}>{provider.status}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-neutral-400 uppercase tracking-wider font-bold">
                    {provider.enabled ? "Active" : "Disabled"}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="p-4 border-t border-neutral-200 bg-neutral-50 flex justify-end">
            <button onClick={onClose} className="px-4 py-2 bg-indigo-600 text-white font-medium rounded-md hover:bg-indigo-700 transition-colors">
              Save Changes
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
