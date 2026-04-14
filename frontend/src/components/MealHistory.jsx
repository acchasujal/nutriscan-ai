import React from 'react';
import { History, Clock, ChevronRight } from 'lucide-react';

const MealHistory = ({ history, onSelect }) => {
  if (!history || history.length === 0) return null;

  const avgScore = history.reduce((acc, curr) => acc + curr.health_score, 0) / history.length;

  return (
    <div className="card">
      <div className="flex-between" style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
          <History size={18} /> Recent Meals
        </h3>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Avg Score: {avgScore.toFixed(1)}/10
        </span>
      </div>

      <div className="stack" style={{ gap: '0.5rem' }}>
        {history.slice(0, 5).map((meal, index) => (
          <div 
            key={meal.id || index} 
            onClick={() => onSelect(meal)}
            style={{ 
              padding: '0.75rem', 
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              backgroundColor: 'var(--surface-color)'
            }}
            onMouseOver={e => e.currentTarget.style.backgroundColor = 'var(--bg-color)'}
            onMouseOut={e => e.currentTarget.style.backgroundColor = 'var(--surface-color)'}
            role="button"
            tabIndex={0}
            aria-label={`View details for ${meal.items[0]}`}
          >
            <div style={{ display: 'flex', alignContent: 'center', gap: '0.75rem' }}>
              <div style={{ 
                width: '32px', height: '32px', borderRadius: '50%', 
                backgroundColor: meal.health_score >= 8 ? '#dcfce7' : meal.health_score >= 5 ? '#fef3c7' : '#fee2e2',
                color: meal.health_score >= 8 ? '#166534' : meal.health_score >= 5 ? '#92400e' : '#991b1b',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.75rem', fontWeight: 600
              }}>
                {Math.round(meal.health_score)}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>{meal.items[0]}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  <Clock size={10} />
                  <span>{new Date(meal.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </div>
              </div>
            </div>
            <ChevronRight size={16} color="var(--text-muted)" />
          </div>
        ))}
      </div>
    </div>
  );
};

export default MealHistory;
