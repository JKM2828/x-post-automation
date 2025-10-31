import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { tweets } from '../services/api';

export default function TweetsPage() {
  const navigate = useNavigate();
  const [allTweets, setAllTweets] = useState([]);
  const [newTweet, setNewTweet] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTweets();
  }, []);

  const loadTweets = async () => {
    try {
      const response = await tweets.getAll();
      setAllTweets(response.data);
    } catch (error) {
      console.error('Failed to load tweets:', error);
    }
  };

  const handleCreateTweet = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await tweets.create({
        text: newTweet,
        scheduled_at: scheduledAt || null,
        media_links: []
      });
      setNewTweet('');
      setScheduledAt('');
      await loadTweets();
      alert('Tweet created successfully!');
    } catch (error) {
      console.error('Failed to create tweet:', error);
      alert('Failed to create tweet');
    } finally {
      setLoading(false);
    }
  };

  const handlePostTweet = async (tweetId) => {
    if (!confirm('Post this tweet now?')) return;
    
    try {
      await tweets.post(tweetId);
      await loadTweets();
      alert('Tweet posted successfully!');
    } catch (error) {
      console.error('Failed to post tweet:', error);
      alert('Failed to post tweet');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <button onClick={() => navigate('/dashboard')} style={{ marginBottom: '20px' }}>← Back to Dashboard</button>
      
      <h1>📝 Tweets</h1>

      {/* Create Tweet Form */}
      <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h2>Create New Tweet</h2>
        <form onSubmit={handleCreateTweet}>
          <div style={{ marginBottom: '15px' }}>
            <textarea
              value={newTweet}
              onChange={(e) => setNewTweet(e.target.value)}
              placeholder="What's happening?"
              required
              maxLength={280}
              style={{
                width: '100%',
                padding: '10px',
                minHeight: '100px',
                borderRadius: '4px',
                border: '1px solid #ddd'
              }}
            />
            <div style={{ textAlign: 'right', fontSize: '14px', color: '#666' }}>
              {newTweet.length}/280
            </div>
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <label>Schedule for later (optional):</label>
            <input
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              style={{ width: '100%', padding: '8px', marginTop: '5px' }}
            />
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
            {loading ? 'Creating...' : 'Create Tweet'}
          </button>
        </form>
      </div>

      {/* Tweets List */}
      <div>
        <h2>All Tweets</h2>
        {allTweets.length === 0 ? (
          <p>No tweets yet.</p>
        ) : (
          <div style={{ display: 'grid', gap: '15px' }}>
            {allTweets.map((tweet) => (
              <div
                key={tweet.id}
                style={{
                  padding: '20px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  backgroundColor: '#f9f9f9'
                }}
              >
                <p style={{ marginBottom: '10px', fontSize: '16px' }}>{tweet.text}</p>
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                  <span>Status: <strong>{tweet.status}</strong></span>
                  {tweet.generated_by_ai && <span style={{ marginLeft: '10px' }}>🤖 AI Generated</span>}
                  {tweet.viral_score && (
                    <span style={{ marginLeft: '10px' }}>
                      Viral Score: {(tweet.viral_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                {tweet.scheduled_at && (
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                    Scheduled: {new Date(tweet.scheduled_at).toLocaleString()}
                  </div>
                )}
                {(tweet.status === 'draft' || tweet.status === 'scheduled') && (
                  <button
                    onClick={() => handlePostTweet(tweet.id)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#1DA1F2',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Post Now
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
