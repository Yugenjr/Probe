import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import { getMe, rotateApiKey } from '../lib/api';
import { useAuth, withAuth } from '../hooks/useAuth';
import { toast } from 'react-hot-toast';
import { Key, AlertTriangle, CheckCircle2, Copy, Eye, EyeOff, Shield, RefreshCw } from 'lucide-react';

function Settings() {
  const { apiKey, setApiKey } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [showKey, setShowKey] = useState(false);
  const [rotating, setRotating] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await getMe();
      setProfile(data);
    } catch (err) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleRotateKey = async () => {
    if (!confirm("WARNING: Rotating your API Key will immediately invalidate your old key. All active SDK deployments using the old key will fail to authenticate until you update them. Are you sure you want to proceed?")) {
      return;
    }

    setRotating(true);
    try {
      const data = await rotateApiKey();
      setApiKey(data.api_key);
      toast.success('API Key rotated successfully!');
      setShowKey(true);
    } catch (err) {
      toast.error(err.message || 'Failed to rotate API Key');
    } finally {
      setRotating(false);
    }
  };

  const copyToClipboard = () => {
    if (navigator.clipboard && apiKey) {
      navigator.clipboard.writeText(apiKey);
      setCopied(true);
      toast.success('API Key copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full min-h-[500px]">
          <div className="w-8 h-8 border-2 border-[var(--border)] border-t-[var(--text-primary)] rounded-full animate-spin"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <Head>
        <title>Settings - DriftGuard</title>
      </Head>

      <div className="w-full py-6">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)] mb-8 tracking-tight">
          Account Settings
        </h1>

        <div className="space-y-8">
          {/* Profile Section */}
          <section className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg overflow-hidden">
            <div className="border-b border-[var(--border)] px-6 py-4">
              <h2 className="text-[14px] font-semibold text-[var(--text-primary)]">Profile Information</h2>
            </div>
            <div className="p-6">
              <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div>
                  <dt className="text-[12px] text-[var(--text-secondary)] mb-1">Full Name</dt>
                  <dd className="text-[14px] text-[var(--text-primary)] font-medium">{profile?.name}</dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--text-secondary)] mb-1">Email Address</dt>
                  <dd className="text-[14px] text-[var(--text-primary)] font-medium">{profile?.email}</dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--text-secondary)] mb-1">Account Created</dt>
                  <dd className="text-[14px] text-[var(--text-primary)] font-medium">{new Date(profile?.created_at).toLocaleDateString()}</dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--text-secondary)] mb-1">Status</dt>
                  <dd>
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-[var(--green-dim)] text-[var(--green)]">
                      Active
                    </span>
                  </dd>
                </div>
              </dl>
            </div>
          </section>

          {/* API Key Management */}
          <section className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg overflow-hidden">
            <div className="border-b border-[var(--border)] px-6 py-4 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Key className="w-4 h-4 text-[var(--text-primary)]" />
                <h2 className="text-[14px] font-semibold text-[var(--text-primary)]">API Key Management</h2>
              </div>
            </div>
            <div className="p-6 space-y-6">
              <p className="text-[13px] text-[var(--text-secondary)] max-w-2xl leading-relaxed">
                Your API key is used to authenticate requests from your SDK deployments to the DriftGuard backend. 
                Keep this key secret and do not expose it in client-side code.
              </p>

              <div className="space-y-2">
                <label className="text-[12px] font-medium text-[var(--text-primary)]">Current Secret Key</label>
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="relative flex-1">
                    <input
                      type={showKey ? "text" : "password"}
                      value={apiKey || ''}
                      readOnly
                      className="block w-full pl-3 pr-10 py-2 border border-[var(--border)] rounded-md bg-[var(--bg-base)] text-[var(--text-primary)] font-mono text-[13px] focus:outline-none focus:ring-2 focus:ring-[var(--border-hover)] transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowKey(!showKey)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                    >
                      {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  <button
                    onClick={copyToClipboard}
                    className="flex items-center justify-center space-x-2 px-4 py-2 bg-black hover:bg-neutral-800 text-white rounded-md font-medium text-[13px] transition-colors sm:w-auto w-full"
                  >
                    {copied ? <CheckCircle2 className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Danger Zone */}
          <section className="bg-[var(--bg-surface)] border border-[var(--red)] rounded-lg overflow-hidden">
            <div className="border-b border-[var(--red)] px-6 py-4">
              <h2 className="text-[14px] font-semibold text-[var(--red)] flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Danger Zone
              </h2>
            </div>
            <div className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
              <div>
                <h3 className="text-[13px] font-semibold text-[var(--text-primary)]">Rotate API Key</h3>
                <p className="text-[13px] text-[var(--text-secondary)] mt-1 max-w-xl leading-relaxed">
                  Instantly invalidate your current API Key and generate a new one. 
                  Any running applications using the old key will lose access immediately.
                </p>
              </div>
              <button
                onClick={handleRotateKey}
                disabled={rotating}
                className="flex items-center justify-center px-4 py-2 bg-[var(--red)] hover:bg-[#c00000] text-white rounded-md font-medium text-[13px] transition-colors whitespace-nowrap disabled:opacity-50"
              >
                {rotating ? (
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Shield className="w-4 h-4 mr-2" />
                )}
                {rotating ? 'Rotating...' : 'Rotate Key'}
              </button>
            </div>
          </section>
        </div>
      </div>
    </Layout>
  );
}

export default withAuth(Settings);
