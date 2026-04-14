import React from 'react';
import { Target } from 'lucide-react';

const ProgressBar = ({ label, currentValue, targetValue, unit, color }) => {
  const percentage = Math.min((currentValue / targetValue) * 100, 100) || 0;
  
  return (
    <div style={{ marginBottom: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
        <span style={{ fontWeight: 500, color: 'var(--text-main)' }}>{label}</span>
        <span style={{ color: 'var(--text-muted)' }}>{Math.round(currentValue)} / {targetValue} {unit}</span>
      </div>
      <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--border-color)', borderRadius: '4px', overflow: 'hidden' }}>
        <div 
          style={{ 
            height: '100%', 
            width: `${percentage}%`, 
            backgroundColor: color,
            transition: 'width 0.5s ease'
          }} 
        />
      </div>
    </div>
  );
};

const DailyTracker = ({ intake, profile }) => {
  // Rough daily targets if not specified
  const proteinTarget = profile?.goal === 'muscle_gain' ? 150 : 80;
  const sodiumTarget = profile?.conditions?.includes('low_sodium') ? 1500 : 2300;
  
  return (
    <div className="card">
      <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', margin: 0 }}>
        <Target size={18} /> Daily Tracker
      </h3>
      
      <ProgressBar 
        label="Calories" 
        currentValue={intake.total_calories} 
        targetValue={profile?.daily_calorie_target || 2000} 
        unit="kcal"
        color="var(--primary)" 
      />
      
      <ProgressBar 
        label="Protein" 
        currentValue={intake.total_protein_g} 
        targetValue={proteinTarget} 
        unit="g"
        color="var(--success)" 
      />
      
      <ProgressBar 
        label="Sodium" 
        currentValue={intake.total_sodium_mg} 
        targetValue={sodiumTarget} 
        unit="mg"
        color="var(--warning)" 
      />
    </div>
  );
};

export default DailyTracker;
