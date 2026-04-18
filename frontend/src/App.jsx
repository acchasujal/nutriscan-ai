import React, { useState, useEffect } from 'react';
import { Apple, Plus, ArrowLeft } from 'lucide-react';

import ImageUploader from './components/ImageUploader';
import HealthScore from './components/HealthScore';
import NutritionGrid from './components/NutritionGrid';
import AdviceCard from './components/AdviceCard';
import MealHistory from './components/MealHistory';
import ProfilePanel from './components/ProfilePanel';
import DailyTracker from './components/DailyTracker';
import AlertsPanel from './components/AlertsPanel';
import BackendHealthPanel from './components/BackendHealthPanel';
import { analyzeMeal } from './api/analyzeMeal';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState({ value: 0, label: 'Preparing image upload...' });
  const [error, setError] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [history, setHistory] = useState([]);
  const [profile, setProfile] = useState(null);
  const [dailyIntake, setDailyIntake] = useState({ total_calories: 0, total_protein_g: 0, total_sodium_mg: 0 });

  useEffect(() => {
    const savedHistory = localStorage.getItem('nutriscan_history');
    if (savedHistory) {
      const parsed = JSON.parse(savedHistory);
      setHistory(parsed);
      calculateDailyIntake(parsed);
    }
  }, []);

  useEffect(() => {
    return () => {
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);

  useEffect(() => {
    if (!loading) {
      setAnalysisProgress({ value: 0, label: 'Preparing image upload...' });
      return undefined;
    }

    const progressPlan = [
      { threshold: 18, label: 'Uploading image...' },
      { threshold: 42, label: 'Checking image quality...' },
      { threshold: 68, label: 'Estimating nutrition...' },
      { threshold: 88, label: 'Personalizing meal insights...' },
      { threshold: 95, label: 'Finalizing your result...' },
    ];

    const interval = setInterval(() => {
      setAnalysisProgress((current) => {
        if (current.value >= 95) {
          return current;
        }

        const nextValue = Math.min(current.value + Math.max(2, Math.ceil((95 - current.value) / 6)), 95);
        const nextStep = progressPlan.find((step) => nextValue <= step.threshold) || progressPlan[progressPlan.length - 1];

        return {
          value: nextValue,
          label: nextStep.label,
        };
      });
    }, 450);

    return () => clearInterval(interval);
  }, [loading]);

  const calculateDailyIntake = (hist) => {
    // Only calculate for today
    const today = new Date().toLocaleDateString();
    const todayMeals = hist.filter(m => new Date(m.timestamp).toLocaleDateString() === today);
    
    setDailyIntake({
      total_calories: todayMeals.reduce((sum, m) => sum + (m.calories || 0), 0),
      total_protein_g: todayMeals.reduce((sum, m) => sum + (m.protein_g || 0), 0),
      total_sodium_mg: todayMeals.reduce((sum, m) => sum + (m.sodium_mg || 0), 0)
    });
  };

  const handleProfileUpdate = (newProfile) => {
    setProfile(newProfile);
  };

  const handleAnalyze = async (file) => {
    console.log(`Starting analysis for file: ${file.name}, size: ${file.size} bytes, type: ${file.type}`);
    
    setLoading(true);
    setAnalysisProgress({ value: 8, label: 'Uploading image...' });
    setError(null);
    setResult(null);
    setImagePreview((currentPreview) => {
      if (currentPreview) {
        URL.revokeObjectURL(currentPreview);
      }

      return URL.createObjectURL(file);
    });
    console.log('Preparing multipart/form-data request to /analyze with the original File object.');

    try {
      const data = await analyzeMeal({
        file,
        profile,
        dailyIntake,
      });
      setAnalysisProgress({ value: 100, label: 'Analysis complete.' });
      
      const resultWithMeta = {
        ...data,
        id: Date.now(),
        timestamp: new Date().toISOString()
      };

      setResult(resultWithMeta);
      
      const updatedHistory = [resultWithMeta, ...history].slice(0, 50); // Keep last 50
      setHistory(updatedHistory);
      localStorage.setItem('nutriscan_history', JSON.stringify(updatedHistory));
      calculateDailyIntake(updatedHistory);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }
    setResult(null);
    setError(null);
    setImagePreview(null);
  };

  return (
    <>
      <header className="flex-between" style={{ marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ padding: '0.5rem', background: 'var(--primary)', borderRadius: 'var(--radius-md)', color: 'white' }}>
            <Apple size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', margin: 0, lineHeight: 1.2 }}>NutriScan Assistant</h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>Advanced AI Nutrition Tracking</p>
          </div>
        </div>
        
        {result && (
          <button className="btn btn-secondary" onClick={reset}>
            <Plus size={16} /> New Scan
          </button>
        )}
      </header>

      <main className="layout-container">
        {/* LEFT COLUMN: Data Entry & Results */}
        <div className="stack">
          {error && (
            <div className="card" style={{ backgroundColor: '#fef2f2', borderColor: '#fecaca', color: '#b91c1c', padding: '1rem' }}>
              {error}
            </div>
          )}

          {!result ? (
            <ImageUploader onUpload={handleAnalyze} loading={loading} progress={analysisProgress} />
          ) : (
            <div className="animate-fade-in stack">
              <div className="flex-between">
                <button className="btn btn-secondary" onClick={reset} aria-label="Back">
                  <ArrowLeft size={16} /> Back
                </button>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {result.items.map((it, idx) => (
                    <span key={idx} style={{ padding: '0.25rem 0.75rem', backgroundColor: 'var(--bg-color)', borderRadius: '1rem', fontSize: '0.75rem', fontWeight: 500, border: '1px solid var(--border-color)' }}>
                      {it}
                    </span>
                  ))}
                </div>
              </div>

              {imagePreview && (
                <div style={{ width: '100%', height: '250px', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
                  <img src={imagePreview} alt="Meal preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: 'minmax(120px, 1fr) 3fr', gap: '1.5rem', alignItems: 'stretch' }}>
                <HealthScore score={result.health_score} />
                <NutritionGrid data={result} />
              </div>

              <AdviceCard concern={result.primary_concern} advice={result.advice} visualConfirmation={result.visual_confirmation} confidence={result.confidence} />
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Profile, Tracking, History */}
        <div className="stack">
          <BackendHealthPanel />
          <AlertsPanel intake={dailyIntake} profile={profile} />
          <DailyTracker intake={dailyIntake} profile={profile} />
          <ProfilePanel onProfileUpdate={handleProfileUpdate} />
          <MealHistory history={history} onSelect={(meal) => { setResult(meal); window.scrollTo(0,0); }} />
        </div>
      </main>
    </>
  );
}

export default App;
