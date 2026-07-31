import React, { useState } from 'react';
import { updateWebhookUrl } from '../lib/api';

export default function WebhookConfig({ modelId, initialUrl = '' }) {
  const [webhookUrl, setWebhookUrl] = useState(initialUrl || '');
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    setSaved(false);
    
    try {
      await updateWebhookUrl(modelId, webhookUrl);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg overflow-hidden font-sans">
      <div className="border-b border-[var(--border)] px-5 py-3 bg-[var(--bg-base)]">
        <h2 className="text-[14px] font-semibold text-[var(--text-primary)]">Webhook Integration</h2>
      </div>
      
      <div className="p-5">
        <p className="text-[13px] text-[var(--text-secondary)] mb-5 max-w-xl leading-relaxed">
          Configure an external orchestrator (like Airflow or Kubeflow) to handle model retraining. DriftGuard will POST a JSON payload to this URL when drift is detected.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={webhookUrl}
            onChange={(e) => setWebhookUrl(e.target.value)}
            placeholder="https://airflow.mycompany.com/api/v1/dags/retrain_model/dagRuns"
            className="flex-1 block w-full px-3 py-2 bg-[var(--bg-base)] border border-[var(--border)] rounded-md text-[13px] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--text-primary)] transition-colors"
          />
          
          <button
            onClick={handleSave}
            disabled={loading}
            className="flex items-center justify-center px-4 py-2 rounded-md font-medium text-[13px] transition-colors bg-black hover:bg-neutral-800 text-white disabled:opacity-50 min-w-[100px]"
          >
            {saved ? 'Saved' : loading ? 'Saving...' : 'Save'}
          </button>
        </div>
        
        {error && (
          <p className="mt-3 text-[13px] text-[var(--red)] font-medium">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
