// ============================================================
// src/components/ApprovalModal.jsx
// Modal for reviewing and approving AI-generated email drafts
// ============================================================

import React from 'react';
import { X, Mail, Building2, Globe, User } from 'lucide-react';

const ApprovalModal = ({ isOpen, onClose, lead, onApprove, onReject, isApproving }) => {
  if (!isOpen || !lead) return null;

  const handleApprove = () => {
    onApprove(lead);
  };

  const handleReject = () => {
    onReject(lead);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Review Email Draft</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Company Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start space-x-3">
              <Building2 className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm text-gray-500">Company</p>
                <p className="font-medium text-gray-900">{lead.company_name}</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Globe className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm text-gray-500">Website</p>
                <a
                  href={lead.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-blue-600 hover:underline"
                >
                  {lead.website_url}
                </a>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <User className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm text-gray-500">Decision Maker</p>
                <p className="font-medium text-gray-900">{lead.decision_maker_name}</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Mail className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium text-gray-900">{lead.verified_email}</p>
              </div>
            </div>
          </div>

          {/* Company Context (AI-enriched info) */}
          {lead.company_context && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Company Context</h3>
              <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md">
                {lead.company_context}
              </p>
            </div>
          )}

          {/* Email Draft */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">AI-Generated Email</h3>
            <textarea
              className="w-full h-64 p-4 text-sm text-gray-700 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              defaultValue={lead.icebreaker_text}
            />
            <p className="text-xs text-gray-500 mt-2">
              You can edit the email above before approving.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t bg-gray-50 rounded-b-lg">
          <button
            onClick={onClose}
            disabled={isApproving}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleReject}
            disabled={isApproving}
            className="px-4 py-2 text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Reject
          </button>
          <button
            onClick={handleApprove}
            disabled={isApproving}
            className="px-6 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {isApproving ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Sending...</span>
              </>
            ) : (
              <>
                <Mail size={18} />
                <span>Approve & Send</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApprovalModal;
