import React from 'react';
import { Target, Activity, Eye } from 'lucide-react';

const AdviceCard = ({ concern, advice, visualConfirmation, confidence }) => {
  return (
    <div className="layout-container" style={{ gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1.5rem', display: 'grid' }}>
      <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--warning)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--text-main)' }}>
          <Target size={18} color="var(--warning)" />
          <h4 style={{ margin: 0, fontSize: '0.875rem', textTransform: 'uppercase' }}>Primary Concern</h4>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.5 }}>{concern}</p>
      </div>

      <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--primary)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--text-main)' }}>
          <Activity size={18} color="var(--primary)" />
          <h4 style={{ margin: 0, fontSize: '0.875rem', textTransform: 'uppercase' }}>Nutritionist Advice</h4>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.5 }}>{advice}</p>
        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', display: 'grid', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', color: 'var(--text-muted)' }}>
            <Eye size={16} style={{ marginTop: '0.1rem', flexShrink: 0 }} />
            <div>
              <strong style={{ color: 'var(--text-main)', fontSize: '0.8rem' }}>What Gemini saw</strong>
              <p style={{ fontSize: '0.82rem', lineHeight: 1.45 }}>{visualConfirmation || 'No visual confirmation returned.'}</p>
            </div>
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            These nutrition numbers are visual estimates, not medical or laboratory measurements. Confidence: {confidence ? `${Math.round(confidence * 100)}%` : 'n/a'}.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdviceCard;
