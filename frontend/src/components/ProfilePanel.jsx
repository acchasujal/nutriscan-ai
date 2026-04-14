import React, { useState, useEffect } from 'react';
import { User, Save } from 'lucide-react';

const defaultProfile = {
  goal: 'maintain',
  diet: 'non-veg',
  conditions: [],
  daily_calorie_target: 2000
};

const ProfilePanel = ({ onProfileUpdate }) => {
  const [profile, setProfile] = useState(defaultProfile);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('nutriscan_profile');
    if (saved) {
      const parsed = JSON.parse(saved);
      setProfile(parsed);
      onProfileUpdate(parsed);
    } else {
      onProfileUpdate(defaultProfile);
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem('nutriscan_profile', JSON.stringify(profile));
    onProfileUpdate(profile);
    setIsEditing(false);
  };

  const handleConditionToggle = (condition) => {
    setProfile(prev => {
      const conditions = prev.conditions.includes(condition)
        ? prev.conditions.filter(c => c !== condition)
        : [...prev.conditions, condition];
      return { ...prev, conditions };
    });
  };

  if (!isEditing) {
    return (
      <div className="card">
        <div className="flex-between mb-4" style={{ marginBottom: '1rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
            <User size={18} /> User Profile
          </h3>
          <button className="btn btn-secondary" onClick={() => setIsEditing(true)}>Edit</button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.875rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Goal:</span>
          <span>{profile.goal.replace('_', ' ')}</span>
          <span style={{ color: 'var(--text-muted)' }}>Diet:</span>
          <span>{profile.diet}</span>
          <span style={{ color: 'var(--text-muted)' }}>Calorie Target:</span>
          <span>{profile.daily_calorie_target} kcal</span>
          <span style={{ color: 'var(--text-muted)' }}>Conditions:</span>
          <span>{profile.conditions.length ? profile.conditions.join(', ') : 'None'}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex-between mb-4" style={{ marginBottom: '1rem' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
          <User size={18} /> Edit Profile
        </h3>
        <button className="btn btn-primary" onClick={handleSave}>
          <Save size={16} /> Save
        </button>
      </div>

      <div className="stack" style={{ gap: '1rem' }}>
        <div>
          <label>Goal</label>
          <select value={profile.goal} onChange={e => setProfile({...profile, goal: e.target.value})}>
            <option value="weight_loss">Weight Loss</option>
            <option value="maintain">Maintain Weight</option>
            <option value="muscle_gain">Muscle Gain</option>
          </select>
        </div>

        <div>
          <label>Diet Type</label>
          <select value={profile.diet} onChange={e => setProfile({...profile, diet: e.target.value})}>
            <option value="veg">Vegetarian</option>
            <option value="non-veg">Non-Vegetarian</option>
          </select>
        </div>

        <div>
          <label>Daily Calorie Target</label>
          <input 
            type="number" 
            value={profile.daily_calorie_target} 
            onChange={e => setProfile({...profile, daily_calorie_target: parseInt(e.target.value) || 2000})}
          />
        </div>

        <div>
          <label>Health Conditions</label>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.25rem' }}>
            {['low_sodium', 'diabetes', 'high_protein'].map(cond => (
              <label key={cond} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontWeight: 'normal' }}>
                <input 
                  type="checkbox" 
                  checked={profile.conditions.includes(cond)}
                  onChange={() => handleConditionToggle(cond)}
                />
                <span style={{ fontSize: '0.8rem', textTransform: 'capitalize' }}>{cond.replace('_', ' ')}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePanel;
