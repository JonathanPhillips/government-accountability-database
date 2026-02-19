import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../utils/api';

interface QueueItem {
  id: string;
  source_url: string;
  source_type: string;
  status: string;
  extracted_data: {
    title?: string;
    author?: string;
    published_date?: string;
  } | null;
  created_at: string;
  updated_at: string;
  auto_processed?: boolean;
  auto_confidence?: string;
  auto_reason?: string;
  keyword_score?: number;
}

interface AutoProcessStats {
  total_items: number;
  auto_processed: number;
  auto_approved: number;
  auto_rejected: number;
  pending_review: number;
  automation_rate: number;
}

interface QueueResponse {
  total: number;
  skip: number;
  limit: number;
  items: QueueItem[];
}

const IngestionQueue: React.FC = () => {
  const [queue, setQueue] = useState<QueueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const [stats, setStats] = useState<AutoProcessStats | null>(null);
  const [processing, setProcessing] = useState(false);
  const limit = 20;

  useEffect(() => {
    fetchQueue();
    fetchStats();
  }, [statusFilter, page]);

  const fetchQueue = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: String(page * limit),
        limit: String(limit),
      });

      if (statusFilter) {
        params.append('status', statusFilter);
      }

      const data = await api.get(`/api/ingestion/?${params}`);
      setQueue(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await api.get('/api/ingestion/auto-process/statistics');
      setStats(data.statistics);
    } catch (err) {
      console.error('Failed to fetch statistics:', err);
    }
  };

  const triggerAutoProcessing = async (dryRun: boolean = false) => {
    if (!dryRun && !confirm('This will automatically approve or reject items based on keyword matching. Continue?')) {
      return;
    }

    try {
      setProcessing(true);
      const data = await api.post(`/api/ingestion/auto-process?limit=1000&dry_run=${dryRun}`, {});

      if (dryRun) {
        const results = data.results;
        alert(
          `Dry Run Results:\n\n` +
          `Total: ${results.total_processed}\n` +
          `Would approve: ${results.approved}\n` +
          `Would reject: ${results.rejected}\n` +
          `Needs review: ${results.review_needed}\n\n` +
          `High confidence: ${results.high_confidence}`
        );
      } else {
        alert(
          `Auto-processing complete!\n\n` +
          `Processed: ${data.results.total_processed} items\n` +
          `Approved: ${data.results.approved}\n` +
          `Rejected: ${data.results.rejected}\n` +
          `Still needs review: ${data.results.review_needed}`
        );
        await fetchQueue();
        await fetchStats();
      }
    } catch (err) {
      alert('Failed to auto-process: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setProcessing(false);
    }
  };

  const triggerAllFeeds = async () => {
    try {
      const data = await api.post('/api/ingestion/tasks/trigger-all-feeds', {});
      alert(`Task queued: ${data.task_id}\nRefresh the page in a few minutes to see new items.`);
    } catch (err) {
      alert('Failed to trigger feeds: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const totalPages = queue ? Math.ceil(queue.total / limit) : 0;

  if (loading && !queue) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <p className="text-gray-600">Loading queue...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ingestion Queue</h1>
          <p className="text-gray-600 mt-1">
            {queue?.total || 0} items awaiting review
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={triggerAllFeeds}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Trigger Feed Ingestion
          </button>
          <Link
            to="/ingestion/add"
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Add Source
          </Link>
        </div>
      </div>

      {/* Auto-Processing Statistics */}
      {stats && (
        <div className="mb-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Auto-Processing Statistics</h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Total Items</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_items}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Auto-Processed</p>
                  <p className="text-2xl font-bold text-purple-600">{stats.auto_processed}</p>
                  <p className="text-xs text-gray-500">{stats.automation_rate.toFixed(1)}% automated</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Auto-Approved</p>
                  <p className="text-2xl font-bold text-green-600">{stats.auto_approved}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Auto-Rejected</p>
                  <p className="text-2xl font-bold text-red-600">{stats.auto_rejected}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Needs Review</p>
                  <p className="text-2xl font-bold text-yellow-600">{stats.pending_review}</p>
                </div>
              </div>
              <div className="mt-3 text-sm text-gray-600">
                <p>Time saved: ~{Math.round(stats.auto_processed * 5 / 60)} hours</p>
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => triggerAutoProcessing(true)}
                disabled={processing}
                className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 disabled:opacity-50 whitespace-nowrap text-sm"
              >
                Dry Run
              </button>
              <button
                onClick={() => triggerAutoProcessing(false)}
                disabled={processing}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 whitespace-nowrap text-sm"
              >
                {processing ? 'Processing...' : 'Auto-Process Queue'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 flex gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status Filter
          </label>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(0);
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="needs_edit">Needs Edit</option>
          </select>
        </div>
      </div>

      {/* Queue Items */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title / Source
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {queue?.items.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <div className="font-medium text-gray-900">
                      {item.extracted_data?.title || 'No title'}
                    </div>
                    {item.extracted_data?.author && (
                      <div className="text-gray-500">
                        by {item.extracted_data.author}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-900">
                    {item.source_type.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex flex-col gap-1">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(item.status)}`}>
                      {item.status}
                    </span>
                    {item.auto_processed && (
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                        🤖 Auto ({item.auto_confidence})
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(item.created_at)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <Link
                    to={`/ingestion/${item.id}`}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Review
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex justify-between items-center">
          <div className="text-sm text-gray-700">
            Showing {page * limit + 1} to {Math.min((page + 1) * limit, queue?.total || 0)} of {queue?.total || 0} results
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default IngestionQueue;
