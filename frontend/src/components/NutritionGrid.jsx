import React from 'react';
import { Flame, Droplets, Zap, Wind, AlertCircle } from 'lucide-react';

const NutritionGrid = ({ data }) => {
  const items = [
    { label: 'Calories', value: data.calories, unit: 'kcal', icon: Flame, color: '#ef4444' },
    { label: 'Protein', value: data.protein_g, unit: 'g', icon: Zap, color: '#3b82f6' },
    { label: 'Carbs', value: data.carbs_g, unit: 'g', icon: Wind, color: '#f59e0b' },
    { label: 'Fat', value: data.fat_g, unit: 'g', icon: Droplets, color: '#10b981' },
    { label: 'Sodium', value: data.sodium_mg, unit: 'mg', icon: AlertCircle, color: '#8b5cf6' },
    { label: 'Confidence', value: data.confidence ? (data.confidence * 100).toFixed(0) : '--', unit: data.confidence ? '%' : '', icon: Zap, color: '#6366f1' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))', gap: '1rem' }}>
      {items.map((item, index) => (
        <div 
          key={item.label} 
          className="card" 
          style={{ 
            padding: '1rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
            boxShadow: 'none'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 500 }}>
            <item.icon size={14} color={item.color} />
            <span style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.label}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.2rem' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)' }}>{item.value}</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.unit}</span>
          </div>
          {item.label === 'Confidence' && (
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Lower confidence means the estimate may be less reliable.
            </span>
          )}
        </div>
      ))}
    </div>
  );
};

export default NutritionGrid;
