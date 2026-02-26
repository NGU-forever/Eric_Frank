// ============================================================
// src/components/StatusBadge.jsx
// Color-coded status badge component
// ============================================================

import React from 'react';

const statusColors = {
  // Prospecting stages
  Scouted: 'bg-gray-100 text-gray-800 border-gray-300',
  Mined: 'bg-blue-100 text-blue-800 border-blue-300',
  Drafted: 'bg-yellow-100 text-yellow-800 border-yellow-300',

  // Approval stages
  Approved: 'bg-green-100 text-green-800 border-green-300',
  Emailed: 'bg-purple-100 text-purple-800 border-purple-300',
  Meeting_Booked: 'bg-amber-100 text-amber-800 border-amber-300',

  // Rejection stages
  Blacklisted: 'bg-red-100 text-red-800 border-red-300',
  Rejected: 'bg-red-100 text-red-800 border-red-300',
};

const StatusBadge = ({ status }) => {
  const colorClass = statusColors[status] || 'bg-gray-100 text-gray-800 border-gray-300';

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${colorClass}`}>
      {status}
    </span>
  );
};

export default StatusBadge;
