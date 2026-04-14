import React from 'react';
import { Target, Activity } from 'lucide-react';

const AdviceCard = ({ concern, advice }) => {
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
      </div>
    </div>
  );
};

export default AdviceCard;
