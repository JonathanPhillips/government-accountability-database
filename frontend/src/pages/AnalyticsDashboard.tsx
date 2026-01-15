import { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { exportAnalyticsCSV } from '../utils/export';

interface AnalyticsData {
  total_incidents: number;
  by_severity: Record<string, number>;
  by_verification: Record<string, number>;
  by_geographic_scope: Record<string, number>;
  recent_30_days: number;
  top_states: Array<{ state: string; count: number }>;
  last_updated: string;
}

interface TimelineData {
  timeline: Array<{ month: string; count: number }>;
  days: number;
}

interface CategoryStats {
  categories: Array<{ name: string; count: number }>;
}

const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [timeline, setTimeline] = useState<TimelineData | null>(null);
  const [categories, setCategories] = useState<CategoryStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [overviewData, timelineData, categoryData] = await Promise.all([
        api.get('/api/analytics/overview'),
        api.get('/api/analytics/timeline?days=365'),
        api.get('/api/analytics/categories')
      ]);

      setAnalytics(overviewData);
      setTimeline(timelineData);
      setCategories(categoryData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string): string => {
    const colors: Record<string, string> = {
      'SeverityEnum.CRITICAL': 'bg-red-500',
      'SeverityEnum.HIGH': 'bg-orange-500',
      'SeverityEnum.MEDIUM': 'bg-yellow-500',
      'SeverityEnum.LOW': 'bg-gray-400'
    };
    return colors[severity] || 'bg-gray-400';
  };

  const getSeverityLabel = (severity: string): string => {
    return severity.replace('SeverityEnum.', '').toLowerCase();
  };

  const getVerificationLabel = (status: string): string => {
    return status.replace('VerificationStatusEnum.', '').toLowerCase();
  };

  const getScopeLabel = (scope: string): string => {
    return scope.replace('GeographicScopeEnum.', '').toLowerCase();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-gray-600">Loading analytics...</div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">Failed to load analytics data</p>
      </div>
    );
  }

  const totalBySeverity = Object.values(analytics.by_severity).reduce((a, b) => a + b, 0);
  const totalByVerification = Object.values(analytics.by_verification).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-4xl font-bold text-gray-900">Analytics Dashboard</h1>
        <div className="flex gap-2">
          <button
            onClick={exportAnalyticsCSV}
            className="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Export Analytics
          </button>
          <button
            onClick={fetchAnalytics}
            className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Refresh Data
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-primary-500">
          <div className="text-gray-500 text-sm font-medium mb-2">Total Incidents</div>
          <div className="text-4xl font-bold text-gray-900">{analytics.total_incidents}</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div className="text-gray-500 text-sm font-medium mb-2">Recent (30 Days)</div>
          <div className="text-4xl font-bold text-gray-900">{analytics.recent_30_days}</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <div className="text-gray-500 text-sm font-medium mb-2">States Affected</div>
          <div className="text-4xl font-bold text-gray-900">{analytics.top_states.length}</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
          <div className="text-gray-500 text-sm font-medium mb-2">Categories</div>
          <div className="text-4xl font-bold text-gray-900">{categories?.categories.length || 0}</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Distribution */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">By Severity</h2>
          <div className="space-y-3">
            {Object.entries(analytics.by_severity).map(([severity, count]) => (
              <div key={severity}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium capitalize">{getSeverityLabel(severity)}</span>
                  <span className="text-gray-600">{count} ({Math.round((count / totalBySeverity) * 100)}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`${getSeverityColor(severity)} h-3 rounded-full transition-all duration-300`}
                    style={{ width: `${(count / totalBySeverity) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Verification Status */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Verification Status</h2>
          <div className="space-y-3">
            {Object.entries(analytics.by_verification).map(([status, count]) => (
              <div key={status}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium capitalize">{getVerificationLabel(status)}</span>
                  <span className="text-gray-600">{count} ({Math.round((count / totalByVerification) * 100)}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${(count / totalByVerification) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Geographic Scope */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Geographic Scope</h2>
          <div className="space-y-3">
            {Object.entries(analytics.by_geographic_scope).map(([scope, count]) => {
              const total = Object.values(analytics.by_geographic_scope).reduce((a, b) => a + b, 0);
              return (
                <div key={scope}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium capitalize">{getScopeLabel(scope)}</span>
                    <span className="text-gray-600">{count} ({Math.round((count / total) * 100)}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${(count / total) * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top States */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Top States by Incident Count</h2>
          <div className="space-y-3">
            {analytics.top_states.slice(0, 10).map((item, index) => {
              const maxCount = analytics.top_states[0]?.count || 1;
              return (
                <div key={item.state}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">#{index + 1} {item.state}</span>
                    <span className="text-gray-600">{item.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-green-500 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${(item.count / maxCount) * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Categories and Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Categories */}
        {categories && categories.categories.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Incidents by Category</h2>
            <div className="space-y-3">
              {categories.categories.slice(0, 8).map((cat) => {
                const maxCount = categories.categories[0]?.count || 1;
                return (
                  <div key={cat.name}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">{cat.name}</span>
                      <span className="text-gray-600">{cat.count}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-indigo-500 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${(cat.count / maxCount) * 100}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Timeline Summary */}
        {timeline && timeline.timeline.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
            <div className="text-sm text-gray-600 mb-4">
              Showing last {timeline.timeline.length} months
            </div>
            <div className="space-y-2">
              {timeline.timeline.slice(-6).reverse().map((item) => (
                <div key={item.month} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-0">
                  <span className="font-medium text-gray-700">{item.month}</span>
                  <span className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-medium">
                    {item.count} incidents
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-500">
        Last updated: {new Date(analytics.last_updated).toLocaleString()}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
