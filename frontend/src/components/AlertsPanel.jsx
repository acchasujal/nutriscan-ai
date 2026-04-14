import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';

const AlertsPanel = ({ intake, profile }) => {
  const alerts = [];

  const sodiumTarget = profile?.conditions?.includes('low_sodium') ? 1500 : 2300;
  if (intake.total_sodium_mg > sodiumTarget) {
    alerts.push({ type: 'error', message: `High Sodium! You've exceeded your daily target of ${sodiumTarget}mg.` });
  }

  if (intake.total_calories > profile?.daily_calorie_target) {
    alerts.push({ type: 'warning', message: `Calorie limit exceeded by ${Math.round(intake.total_calories - profile.daily_calorie_target)} kcal.` });
  }

  // Only show low protein if they've eaten a significant amount of food but lacking protein
  const proteinTarget = profile?.goal === 'muscle_gain' ? 150 : 80;
  if (intake.total_calories > 1000 && intake.total_protein_g < (proteinTarget / 2)) {
    alerts.push({ type: 'info', message: `Low protein intake. Consider adding a protein-rich snack.` });
  }

  if (alerts.length === 0) {
    return null;
  }

  return (
    <div className="stack" style={{ gap: '0.75rem' }}>
      {alerts.map((alert, idx) => {
        let bgColor, borderColor, textColor, Icon;
        
        switch(alert.type) {
          case 'error':
            bgColor = '#fef2f2'; borderColor = '#fecaca'; textColor = '#b91c1c'; Icon = AlertTriangle; break;
          case 'warning':
            bgColor = '#fffbeb'; borderColor = '#fde68a'; textColor = '#b45309'; Icon = AlertTriangle; break;
          default:
            bgColor = '#eff6ff'; borderColor = '#bfdbfe'; textColor = '#1d4ed8'; Icon = Info; break;
        }

        return (
          <div key={idx} style={{ 
            backgroundColor: bgColor, 
            border: `1px solid ${borderColor}`,
            color: textColor,
            padding: '1rem',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.75rem',
            fontSize: '0.875rem',
            fontWeight: 500
          }}>
            <Icon size={18} style={{ flexShrink: 0, marginTop: '0.125rem' }} />
            <span>{alert.message}</span>
          </div>
        )
      })}
    </div>
  );
};

export default AlertsPanel;
