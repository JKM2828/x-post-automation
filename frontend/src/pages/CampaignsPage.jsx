import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { campaigns } from '../services/api';

export default function CampaignsPage() {
  const navigate = useNavigate();
  const [allCampaigns, setAllCampaigns] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    recurrence: '',
    slots: []
  });

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      const response = await campaigns.getAll();
      setAllCampaigns(response.data);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await campaigns.create(formData);
      setFormData({ name: '', description: '', recurrence: '', slots: [] });
      setShowForm(false);
      await loadCampaigns();
      alert('Campaign created successfully!');
    } catch (error) {
      console.error('Failed to create campaign:', error);
      alert('Failed to create campaign');
    }
  };

  const handleToggle = async (id) => {
    try {
      await campaigns.toggle(id);
      await loadCampaigns();
    } catch (error) {
      console.error('Failed to toggle campaign:', error);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this campaign?')) return;
    
    try {
      await campaigns.delete(id);
      await loadCampaigns();
    } catch (error) {
      console.error('Failed to delete campaign:', error);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <button onClick={() => navigate('/dashboard')} style={{ marginBottom: '20px' }}>← Back to Dashboard</button>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>🎯 Campaigns</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            padding: '10px 20px',
            backgroundColor: '#1DA1F2',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {showForm ? 'Cancel' : '+ New Campaign'}
        </button>
      </div>

      {/* Create Campaign Form */}
      {showForm && (
        <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h2>Create New Campaign</h2>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '15px' }}>
              <label>Campaign Name:</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                style={{ width: '100%', padding: '10px', marginTop: '5px' }}
              />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label>Description:</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                style={{ width: '100%', padding: '10px', marginTop: '5px', minHeight: '80px' }}
              />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label>Recurrence (Cron Expression):</label>
              <input
                type="text"
                value={formData.recurrence}
                onChange={(e) => setFormData({ ...formData, recurrence: e.target.value })}
                placeholder="e.g., 0 9 * * * (daily at 9 AM)"
                style={{ width: '100%', padding: '10px', marginTop: '5px' }}
              />
            </div>

            <button
              type="submit"
              style={{
                padding: '10px 20px',
                backgroundColor: '#1DA1F2',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Create Campaign
            </button>
          </form>
        </div>
      )}

      {/* Campaigns List */}
      <div>
        <h2>All Campaigns</h2>
        {allCampaigns.length === 0 ? (
          <p>No campaigns yet. Create your first campaign!</p>
        ) : (
          <div style={{ display: 'grid', gap: '15px' }}>
            {allCampaigns.map((campaign) => (
              <div
                key={campaign.id}
                style={{
                  padding: '20px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  backgroundColor: campaign.active ? '#f0f8ff' : '#f9f9f9'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <h3 style={{ margin: 0 }}>{campaign.name}</h3>
                  <span style={{
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontSize: '14px',
                    backgroundColor: campaign.active ? '#4CAF50' : '#999',
                    color: 'white'
                  }}>
                    {campaign.active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                <p style={{ color: '#666', marginBottom: '10px' }}>{campaign.description}</p>
                
                {campaign.recurrence && (
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                    Recurrence: <code>{campaign.recurrence}</code>
                  </div>
                )}
                
                <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
                  <button
                    onClick={() => handleToggle(campaign.id)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: campaign.active ? '#999' : '#4CAF50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    {campaign.active ? 'Deactivate' : 'Activate'}
                  </button>
                  <button
                    onClick={() => handleDelete(campaign.id)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#f44336',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
