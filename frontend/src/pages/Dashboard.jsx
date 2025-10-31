import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { analytics, tweets } from '../services/api';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [recentTweets, setRecentTweets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [summaryRes, tweetsRes] = await Promise.all([
        analytics.getSummary(30),
        tweets.getAll(null, 10)
      ]);
      setSummary(summaryRes.data);
      setRecentTweets(tweetsRes.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading...</div>;
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '30px' }}>
        <h1>🐦 Dashboard</h1>
        <div>
          <span style={{ marginRight: '20px' }}>Welcome, {user?.username}!</span>
          <button onClick={handleLogout} style={{ padding: '8px 16px' }}>Logout</button>
        </div>
      </div>

      {/* Navigation */}
      <div style={{ marginBottom: '30px' }}>
        <button onClick={() => navigate('/dashboard')} style={{ marginRight: '10px', padding: '8px 16px' }}>Dashboard</button>
        <button onClick={() => navigate('/tweets')} style={{ marginRight: '10px', padding: '8px 16px' }}>Tweets</button>
        <button onClick={() => navigate('/ai-generate')} style={{ marginRight: '10px', padding: '8px 16px' }}>AI Generate</button>
        <button onClick={() => navigate('/campaigns')} style={{ padding: '8px 16px' }}>Campaigns</button>
      </div>

      {/* Stats */}
      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '30px' }}>
          <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
            <h3>Total Tweets</h3>
            <p style={{ fontSize: '32px', fontWeight: 'bold' }}>{summary.total_tweets}</p>
          </div>
          <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
            <h3>Total Engagement</h3>
            <p style={{ fontSize: '32px', fontWeight: 'bold' }}>{summary.total_engagement}</p>
          </div>
          <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
            <h3>Avg Engagement</h3>
            <p style={{ fontSize: '32px', fontWeight: 'bold' }}>
              {(summary.avg_engagement_rate * 100).toFixed(2)}%
            </p>
          </div>
          <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
            <h3>Best Hour</h3>
            <p style={{ fontSize: '32px', fontWeight: 'bold' }}>
              {summary.best_time_slots[0]?.hour || 'N/A'}:00
            </p>
          </div>
        </div>
      )}

      {/* Recent Tweets */}
      <div>
        <h2>Recent Tweets</h2>
        {recentTweets.length === 0 ? (
          <p>No tweets yet. Start creating!</p>
        ) : (
          <div style={{ display: 'grid', gap: '10px' }}>
            {recentTweets.map((tweet) => (
              <div
                key={tweet.id}
                style={{
                  padding: '15px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  backgroundColor: '#f9f9f9'
                }}
              >
                <p style={{ marginBottom: '10px' }}>{tweet.text}</p>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', color: '#666' }}>
                  <span>Status: {tweet.status}</span>
                  <span>{tweet.generated_by_ai && '🤖 AI Generated'}</span>
                  {tweet.viral_score && <span>Viral Score: {(tweet.viral_score * 100).toFixed(0)}%</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
