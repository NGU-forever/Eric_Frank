// ============================================================
// src/components/LeadsTable.jsx
// Table display for leads with review actions
// ============================================================

import React, { useState, useEffect } from 'react';
import { RefreshCw, Eye, FileText, Building2, Globe, Mail, Phone } from 'lucide-react';
import { leadsApi } from '../api/leadsApi';
import StatusBadge from './StatusBadge';

const LeadsTable = ({ onReview, currentThreadId }) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLeads = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await leadsApi.listLeads({ limit: 50 });
      setLeads(Array.isArray(data) ? data : data.leads || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch leads');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchLeads, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleReview = (lead) => {
    if (onReview) {
      onReview(lead);
    }
  };

  const getActionButton = (lead) => {
    // Drafted leads need review
    if (lead.lead_status === 'Drafted' && !lead.is_approved) {
      return (
        <button
          onClick={() => handleReview(lead)}
          className="px-3 py-1.5 text-sm text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors flex items-center space-x-1"
        >
          <FileText size={16} />
          <span>Review</span>
        </button>
      );
    }

    // Other leads show view details
    return (
      <button
        onClick={() => handleReview(lead)}
        className="px-3 py-1.5 text-sm text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors flex items-center space-x-1"
      >
        <Eye size={16} />
        <span>View Details</span>
      </button>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b">
        <h2 className="text-2xl font-bold text-gray-900">Leads</h2>
        {currentThreadId && (
          <span className="text-sm text-gray-500">
            Active Thread: <code className="bg-gray-100 px-2 py-1 rounded">{currentThreadId}</code>
          </span>
        )}
        <button
          onClick={fetchLeads}
          disabled={loading}
          className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
          title="Refresh leads"
        >
          <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 border-b border-red-200">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Decision Maker
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                  <RefreshCw size={24} className="mx-auto mb-2 animate-spin" />
                  <p>Loading leads...</p>
                </td>
              </tr>
            ) : leads.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                  <Building2 size={24} className="mx-auto mb-2 text-gray-400" />
                  <p>No leads found. Start a campaign to generate leads.</p>
                </td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <Building2 className="w-5 h-5 text-gray-400" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{lead.company_name}</div>
                        <a
                          href={lead.website_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline flex items-center space-x-1"
                        >
                          <Globe size={12} />
                          <span>{new URL(lead.website_url).hostname}</span>
                        </a>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{lead.decision_maker_name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <Mail size={14} />
                        <span className="truncate max-w-[150px]">{lead.verified_email}</span>
                      </div>
                      {lead.whatsapp_number && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Phone size={14} />
                          <span>{lead.whatsapp_number}</span>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={lead.lead_status} />
                    {lead.is_approved && (
                      <span className="ml-2 text-xs text-green-600 font-medium">✓ Approved</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {getActionButton(lead)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination info */}
      {!loading && leads.length > 0 && (
        <div className="px-6 py-4 border-t bg-gray-50 text-sm text-gray-500">
          Showing {leads.length} leads
        </div>
      )}
    </div>
  );
};

export default LeadsTable;
