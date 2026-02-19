import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../utils/api';

interface QueueItem {
  id: string;
  source_url: string;
  source_type: string;
  raw_content: string;
  extracted_data: {
    title?: string;
    author?: string;
    published_date?: string;
    [key: string]: any;
  } | null;
  status: string;
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_incident_id: string | null;
  created_at: string;
  updated_at: string;
}

const IngestionQueueDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [item, setItem] = useState<QueueItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchItem();
  }, [id]);

  const fetchItem = async () => {
    try {
      setLoading(true);
      const data = await api.get(`/api/ingestion/${id}`);
      setItem(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (newStatus: string) => {
    if (!item) return;

    try {
      setUpdating(true);
      const updated = await api.put(`/api/ingestion/${item.id}`, {
        status: newStatus,
      });
      setItem(updated);
      alert('Status updated successfully');
    } catch (err) {
      alert('Failed to update: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setUpdating(false);
    }
  };

  const deleteItem = async () => {
    if (!item || !confirm('Are you sure you want to delete this item?')) return;

    try {
      setUpdating(true);
      await api.delete(`/api/ingestion/${item.id}`);
      alert('Item deleted successfully');
      navigate('/ingestion');
    } catch (err) {
      alert('Failed to delete: ' + (err instanceof Error ? err.message : 'Unknown error'));
      setUpdating(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'needs_edit': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error: {error || 'Item not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-6">
        <button
          onClick={() => navigate('/ingestion')}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Queue
        </button>

        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {item.extracted_data?.title || 'No Title'}
            </h1>
            {item.extracted_data?.author && (
              <p className="text-gray-600 mt-1">by {item.extracted_data.author}</p>
            )}
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(item.status)}`}>
            {item.status}
          </span>
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Metadata</h2>
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">Source Type</dt>
            <dd className="mt-1 text-sm text-gray-900">{item.source_type.replace(/_/g, ' ')}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Created</dt>
            <dd className="mt-1 text-sm text-gray-900">{formatDate(item.created_at)}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Updated</dt>
            <dd className="mt-1 text-sm text-gray-900">{formatDate(item.updated_at)}</dd>
          </div>
          {item.extracted_data?.published_date && (
            <div>
              <dt className="text-sm font-medium text-gray-500">Published</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {formatDate(item.extracted_data.published_date)}
              </dd>
            </div>
          )}
          <div className="col-span-2">
            <dt className="text-sm font-medium text-gray-500">Source URL</dt>
            <dd className="mt-1 text-sm text-gray-900">
              <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                {item.source_url}
              </a>
            </dd>
          </div>
        </dl>
      </div>

      {/* Content Preview */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Content</h2>
        <div className="prose max-w-none">
          <div className="text-sm text-gray-700 whitespace-pre-wrap max-h-96 overflow-y-auto border border-gray-200 rounded p-4">
            {item.raw_content}
          </div>
        </div>
      </div>

      {/* Extracted Data */}
      {item.extracted_data && Object.keys(item.extracted_data).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Extracted Data</h2>
          <pre className="text-sm bg-gray-50 p-4 rounded overflow-x-auto">
            {JSON.stringify(item.extracted_data, null, 2)}
          </pre>
        </div>
      )}

      {/* Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Actions</h2>
        <div className="flex gap-3">
          {item.status === 'pending' && (
            <>
              <button
                onClick={() => updateStatus('approved')}
                disabled={updating}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                Approve
              </button>
              <button
                onClick={() => updateStatus('rejected')}
                disabled={updating}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                Reject
              </button>
              <button
                onClick={() => updateStatus('needs_edit')}
                disabled={updating}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Needs Edit
              </button>
            </>
          )}
          {item.status !== 'pending' && (
            <button
              onClick={() => updateStatus('pending')}
              disabled={updating}
              className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
            >
              Reset to Pending
            </button>
          )}
          <button
            onClick={deleteItem}
            disabled={updating}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 ml-auto"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default IngestionQueueDetail;
