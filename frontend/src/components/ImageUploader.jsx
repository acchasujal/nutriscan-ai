import React from 'react';
import { UploadCloud, Camera, Image as ImageIcon } from 'lucide-react';

const ImageUploader = ({ onUpload, loading }) => {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) onUpload(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      onUpload(file);
    }
  };

  return (
    <div className="card" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
      <div 
        className="animate-fade-in" 
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        style={{
          border: '2px dashed var(--border-color)',
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1rem',
          padding: '2.5rem',
          cursor: loading ? 'not-allowed' : 'pointer',
          backgroundColor: 'var(--bg-color)'
        }}
        onClick={() => document.getElementById('file-upload').click()}
      >
        <input 
          id="file-upload"
          type="file" 
          accept="image/*" 
          onChange={handleFileChange} 
          style={{ display: 'none' }}
          disabled={loading}
        />
        
        <div style={{
          backgroundColor: loading ? 'var(--border-color)' : '#eff6ff',
          padding: '1rem',
          borderRadius: '50%',
          color: loading ? 'var(--text-muted)' : 'var(--primary)'
        }}>
          {loading ? (
            <div className="animate-spin" style={{ width: '24px', height: '24px', border: '2px solid var(--primary)', borderTopColor: 'transparent', borderRadius: '50%' }}></div>
          ) : (
            <UploadCloud size={32} />
          )}
        </div>

        <div>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem', color: 'var(--text-main)' }}>
            {loading ? 'Analyzing...' : 'Upload Meal Photo'}
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Drag and drop or click to browse
          </p>
        </div>

        {!loading && (
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }} onClick={e => e.stopPropagation()}>
            <button className="btn btn-primary" onClick={() => document.getElementById('file-upload').click()} aria-label="Take a photo">
              <Camera size={16} /> Use Camera
            </button>
            <button className="btn btn-secondary" onClick={() => document.getElementById('file-upload').click()} aria-label="Upload from gallery">
              <ImageIcon size={16} /> Browse Gallery
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageUploader;
