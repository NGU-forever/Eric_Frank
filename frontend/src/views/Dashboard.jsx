// ============================================================
// src/views/Dashboard.jsx
// Main dashboard view with campaign and leads tabs
// ============================================================

import React, { useState } from 'react';
import { Rocket, Users } from 'lucide-react';
import CampaignPage from '../components/CampaignPage';
import LeadsTable from '../components/LeadsTable';
import ApprovalModal from '../components/ApprovalModal';
import { leadsApi } from '../api/leadsApi';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('campaign'); // 'campaign' | 'leads'
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [selectedLead, setSelectedLead] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isApproving, setIsApproving] = useState(false);

  const handleWorkflowStarted = (threadId) => {
    setCurrentThreadId(threadId);
    // Auto-switch to leads tab after 2 seconds
    setTimeout(() => {
      setActiveTab('leads');
    }, 2000);
  };

  const handleReviewLead = (lead) => {
    setSelectedLead(lead);
    setIsModalOpen(true);
  };

  const handleApproveDraft = async (lead) => {
    if (!currentThreadId) {
      alert('No active thread. Please start a new campaign.');
      return;
    }

    setIsApproving(true);

    try {
      await leadsApi.approveDraft(lead.id, currentThreadId);
      setIsModalOpen(false);
      setSelectedLead(null);
      // Refresh leads by switching to leads tab
      setActiveTab('leads');
    } catch (err) {
      alert(`Failed to approve draft: ${err.message}`);
    } finally {
      setIsApproving(false);
    }
  };

  const handleRejectDraft = (lead) => {
    // For now, just close the modal
    // In production, you might want to call a rejection API
    setIsModalOpen(false);
    setSelectedLead(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">B2B AI Outreach Dashboard</h1>
              <p className="text-sm text-gray-500">Automated prospecting and email campaigns</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8">
              <button
                onClick={() => setActiveTab('campaign')}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'campaign'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Rocket size={18} />
                <span>Campaign</span>
              </button>
              <button
                onClick={() => setActiveTab('leads')}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'leads'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Users size={18} />
                <span>Leads</span>
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'campaign' && (
          <CampaignPage onWorkflowStarted={handleWorkflowStarted} />
        )}

        {activeTab === 'leads' && (
          <LeadsTable
            onReview={handleReviewLead}
            currentThreadId={currentThreadId}
          />
        )}
      </main>

      {/* Approval Modal */}
      <ApprovalModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedLead(null);
        }}
        lead={selectedLead}
        onApprove={handleApproveDraft}
        onReject={handleRejectDraft}
        isApproving={isApproving}
      />
    </div>
  );
};

export default Dashboard;
