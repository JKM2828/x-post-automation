import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ai } from '../services/api';

export default function AIGeneratePage() {
  const navigate = useNavigate();
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('professional');
  const [numVariants, setNumVariants] = useState(3);
  const [includeHashtags, setIncludeHashtags] = useState(true);
  const [includeCta, setIncludeCta] = useState(true);
  const [loading, setLoading] = useState(false);
  const [variants, setVariants] = useState([]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await ai.generate({
        topic,
        tone,
        num_variants: numVariants,
        include_hashtags: includeHashtags,
        include_cta: includeCta
      });
      setVariants(response.data.variants);
    } catch (error) {
      console.error('Failed to generate:', error);
      alert('Failed to generate tweets. Make sure GEMINI_API_KEY is configured.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <button onClick={() => navigate('/dashboard')} style={{ marginBottom: '20px' }}>← Back to Dashboard</button>
      
      <h1>🤖 AI Tweet Generator</h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>
        Generate viral tweets using Google Gemini AI
      </p>

      {/* Generation Form */}
      <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <form onSubmit={handleGenerate}>
          <div style={{ marginBottom: '15px' }}>
            <label>Topic:</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., AI and future of work"
              required
              style={{ width: '100%', padding: '10px', marginTop: '5px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label>Tone:</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              style={{ width: '100%', padding: '10px', marginTop: '5px' }}
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="humorous">Humorous</option>
              <option value="inspirational">Inspirational</option>
            </select>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label>Number of Variants (1-5):</label>
            <input
              type="number"
              value={numVariants}
              onChange={(e) => setNumVariants(Number(e.target.value))}
              min="1"
              max="5"
              style={{ width: '100%', padding: '10px', marginTop: '5px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'flex', alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={includeHashtags}
                onChange={(e) => setIncludeHashtags(e.target.checked)}
                style={{ marginRight: '10px' }}
              />
              Include Hashtags
            </label>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'flex', alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={includeCta}
                onChange={(e) => setIncludeCta(e.target.checked)}
                style={{ marginRight: '10px' }}
              />
              Include Call-to-Action
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '10px 20px',
              backgroundColor: '#1DA1F2',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Generating...' : 'Generate Tweets'}
          </button>
        </form>
      </div>

      {/* Generated Variants */}
      {variants.length > 0 && (
        <div>
          <h2>Generated Tweets</h2>
          <p style={{ color: '#666', marginBottom: '15px' }}>
            These tweets have been saved as drafts. Go to Tweets page to post them.
          </p>
          <div style={{ display: 'grid', gap: '15px' }}>
            {variants.map((variant, index) => (
              <div
                key={index}
                style={{
                  padding: '20px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  backgroundColor: '#f0f8ff'
                }}
              >
                <p style={{ marginBottom: '10px', fontSize: '16px' }}>{variant.text}</p>
                <div style={{ fontSize: '14px', color: '#666' }}>
                  <span>Viral Score: <strong>{(variant.viral_score * 100).toFixed(0)}%</strong></span>
                  <span style={{ marginLeft: '10px' }}>🤖 AI Generated</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
