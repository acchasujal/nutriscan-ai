import React, { useEffect, useState } from 'react';
import { checkBackendHealth } from '../api/analyzeMeal';
import { Activity, CheckCircle2, XCircle, X } from 'lucide-react';

export default function DebugPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    if (!isOpen) return;

    const fetchHealth = async () => {
      const data = await checkBackendHealth();
      setHealth(data);
    };
    fetchHealth();
    
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [isOpen]);

  if (!health && !isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        title="Debug Mode"
        style={{
          position: 'fixed',
          bottom: '1.5rem',
          right: '1.5rem',
          width: '44px',
          height: '44px',
          borderRadius: '50%',
          background: 'var(--primary)',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 99,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          transition: 'all 0.2s ease',
          opacity: 0.7,
          fontSize: '0.75rem',
          fontWeight: 600,
        }}
        onMouseEnter={(e) => {
          e.target.style.opacity = '1';
          e.target.style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          e.target.style.opacity = '0.7';
          e.target.style.transform = 'scale(1)';
        }}
      >
        🔧
      </button>
    );
  }

  if (!isOpen) return null;

  const isOk = health?.status === 'ok';
  const geminiOk = health?.gemini_model === 'working';
  const geminiLabel = geminiOk ? 'Successful' : 'Not working';
  const geminiColor = geminiOk ? '#10b981' : '#ef4444';

  return (
    <>
      {/* Overlay */}
      <div
        onClick={() => setIsOpen(false)}
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          zIndex: 100,
          cursor: 'pointer',
        }}
      />

      {/* Modal */}
      <div
        style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          background: 'var(--bg-color)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
          zIndex: 101,
          width: '100%',
          maxWidth: '320px',
          padding: '1.5rem',
          animation: 'slideUp 0.2s ease',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={18} style={{ color: isOk ? '#10b981' : '#ef4444' }} />
            <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>Backend Status</h3>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '0.25rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              transition: 'color 0.2s',
            }}
            onMouseEnter={(e) => (e.target.style.color = 'var(--text-main)')}
            onMouseLeave={(e) => (e.target.style.color = 'var(--text-muted)')}
          >
            <X size={18} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>API Key:</span>
            <span>
              {health?.api_key_loaded ? (
                <CheckCircle2 size={16} color="#10b981" />
              ) : (
                <XCircle size={16} color="#ef4444" />
              )}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Gemini:</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: geminiColor }}>
              {geminiOk ? (
                <CheckCircle2 size={16} color="#10b981" />
              ) : (
                <XCircle size={16} color="#ef4444" />
              )}
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
            <span style={{ color: 'var(--text-muted)', textAlign: 'right', fontSize: '0.8rem' }}>
              {health?.gemini_model_name || '--'}
            </span>
          </div>

          <div
            style={{
              padding: '0.75rem',
              borderRadius: '0.5rem',
              background: isOk ? '#ecfdf5' : '#fef2f2',
              color: isOk ? '#166534' : '#b91c1c',
              border: `1px solid ${isOk ? '#a7f3d0' : '#fecaca'}`,
              fontSize: '0.8rem',
              marginTop: '0.5rem',
            }}
          >
            {health?.gemini_message || (isOk ? 'Successful' : 'Gemini is not working.')}
          </div>
        </div>

        <style>{`
          @keyframes slideUp {
            from {
              opacity: 0;
              transform: translateY(10px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `}</style>
      </div>
    </>
  );
}
