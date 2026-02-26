// ============================================================
// src/api/leadsApi.js
// API client for B2B AI Outreach backend
// ============================================================

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export const leadsApi = {
  /**
   * Trigger B2B prospecting workflow with a product keyword
   * @param {string} productKeyword - The product/service to prospect for
   * @param {string|null} competitorDomain - Optional competitor domain
   * @returns {Promise} Response with thread_id
   */
  runWorkflow: async (productKeyword, competitorDomain = null) => {
    const res = await fetch(`${API_BASE}/run_workflow`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_keyword: productKeyword,
        competitor_domain: competitorDomain,
      }),
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to run workflow');
    }

    return res.json();
  },

  /**
   * List leads with optional filters
   * @param {Object} filters - Query parameters { status, is_approved, limit, offset }
   * @returns {Promise} List of leads
   */
  listLeads: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.is_approved !== undefined) params.append('is_approved', String(filters.is_approved));
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.offset) params.append('offset', filters.offset);

    const res = await fetch(`${API_BASE}/leads?${params}`);

    if (!res.ok) {
      throw new Error('Failed to fetch leads');
    }

    return res.json();
  },

  /**
   * Get a single lead by ID
   * @param {string} leadId - UUID of the lead
   * @returns {Promise} Lead details
   */
  getLead: async (leadId) => {
    const res = await fetch(`${API_BASE}/leads/${leadId}`);

    if (!res.ok) {
      throw new Error('Failed to fetch lead');
    }

    return res.json();
  },

  /**
   * Approve a draft and resume the workflow
   * @param {string} leadId - UUID of the lead
   * @param {string} threadId - LangGraph thread ID
   * @returns {Promise} Approval response
   */
  approveDraft: async (leadId, threadId) => {
    const res = await fetch(`${API_BASE}/approve_draft`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lead_id: leadId,
        thread_id: threadId,
      }),
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to approve draft');
    }

    return res.json();
  },

  /**
   * Health check
   * @returns {Promise} Health status
   */
  healthCheck: async () => {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  },
};
