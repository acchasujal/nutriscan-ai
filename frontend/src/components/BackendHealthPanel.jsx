import React, { useEffect, useState } from 'react';
import { checkBackendHealth } from '../api/analyzeMeal';
import { Activity, CheckCircle2, XCircle } from 'lucide-react';

export default function BackendHealthPanel() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      const data = await checkBackendHealth();
      setHealth(data);
    };
    fetchHealth();
    
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  if (!health) return null;

  const isOk = health.status === 'ok';
  const geminiOk = health.gemini_model === 'working';
  const geminiLabel = geminiOk ? 'Successful' : 'Not working';
  const geminiColor = geminiOk ? '#10b981' : '#ef4444';

  return (
    <div className="card" style={{ marginBottom: '1rem', padding: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
        <Activity size={18} style={{ color: isOk ? '#10b981' : '#ef4444' }} />
        <h3 style={{ margin: 0, fontSize: '1rem' }}>Backend Status</h3>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>API Key:</span>
          <span>
            {health.api_key_loaded ? <CheckCircle2 size={16} color="#10b981" /> : <XCircle size={16} color="#ef4444" />}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Gemini:</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: geminiColor }}>
            {geminiOk ? <CheckCircle2 size={16} color="#10b981" /> : <XCircle size={16} color="#ef4444" />}
            {geminiLabel}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 500 }}>
          <span>Status:</span>
          <span style={{ color: isOk ? '#10b981' : '#ef4444' }}>
            {isOk ? 'Running' : 'Error'}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Model:</span>
          <span style={{ color: 'var(--text-muted)', textAlign: 'right' }}>
            {health.gemini_model_name || '--'}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Pre-flight Debug:</span>
          <span style={{ color: health.preflight_debug_enabled ? '#d97706' : '#10b981' }}>
            {health.preflight_debug_enabled ? 'Enabled' : 'Off'}
          </span>
        </div>
        <div style={{ padding: '0.75rem', borderRadius: '0.75rem', background: isOk ? '#ecfdf5' : '#fef2f2', color: isOk ? '#166534' : '#b91c1c', border: `1px solid ${isOk ? '#a7f3d0' : '#fecaca'}` }}>
          {health.gemini_message || (isOk ? 'Successful' : 'Gemini is not working.')}
        </div>
      </div>
    </div>
  );
}
