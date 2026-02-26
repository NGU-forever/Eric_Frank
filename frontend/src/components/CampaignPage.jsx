// ============================================================
// src/components/CampaignPage.jsx
// Form to trigger AI prospecting workflow
// ============================================================

import React, { useState } from 'react';
import { Play, AlertCircle } from 'lucide-react';
import { leadsApi } from '../api/leadsApi';

const CampaignPage = ({ onWorkflowStarted }) => {
  const [productKeyword, setProductKeyword] = useState('');
  const [competitorDomain, setCompetitorDomain] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!productKeyword.trim()) {
      setError('Please enter a product keyword');
      return;
    }

    setIsRunning(true);
    setError(null);
    setMessage(null);

    try {
      const result = await leadsApi.runWorkflow(
        productKeyword,
        competitorDomain || null
      );

      setMessage({
        type: 'success',
        text: `Workflow started successfully! Thread ID: ${result.thread_id}`,
        threadId: result.thread_id,
      });

      // Reset form
      setProductKeyword('');
      setCompetitorDomain('');

      // Notify parent component
      if (onWorkflowStarted) {
        onWorkflowStarted(result.thread_id);
      }
    } catch (err) {
      setError(err.message || 'Failed to start workflow');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Start AI Prospecting</h2>

        {/* Success Message */}
        {message && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm text-green-800">{message.text}</p>
            <p className="text-xs text-green-600 mt-1">
              Thread ID: <code className="bg-green-100 px-1 rounded">{message.threadId}</code>
            </p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="productKeyword" className="block text-sm font-medium text-gray-700 mb-1">
              Product Keyword <span className="text-red-500">*</span>
            </label>
            <input
              id="productKeyword"
              type="text"
              value={productKeyword}
              onChange={(e) => setProductKeyword(e.target.value)}
              placeholder="e.g., LED Lights, SaaS Analytics Platform"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isRunning}
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter the product or service you want to prospect for
            </p>
          </div>

          <div>
            <label htmlFor="competitorDomain" className="block text-sm font-medium text-gray-700 mb-1">
              Competitor Domain <span className="text-gray-400">(optional)</span>
            </label>
            <input
              id="competitorDomain"
              type="text"
              value={competitorDomain}
              onChange={(e) => setCompetitorDomain(e.target.value)}
              placeholder="e.g., competitor.com"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isRunning}
            />
            <p className="text-xs text-gray-500 mt-1">
              Optionally provide a competitor domain to find similar companies
            </p>
          </div>

          <button
            type="submit"
            disabled={isRunning}
            className="w-full flex items-center justify-center space-x-2 px-6 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isRunning ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Starting Workflow...</span>
              </>
            ) : (
              <>
                <Play size={20} />
                <span>Start AI Prospecting</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CampaignPage;
