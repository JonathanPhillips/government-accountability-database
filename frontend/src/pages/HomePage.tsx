import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { incidentsApi } from '../services/api';
import type { IncidentListItem } from '../types';

const HomePage = () => {
  const [recentIncidents, setRecentIncidents] = useState<IncidentListItem[]>([]);
  const [stats, setStats] = useState({ total: 0, critical: 0, high: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await incidentsApi.list({ limit: 5 });
        setRecentIncidents(response.items);
        setStats({
          total: response.total,
          critical: response.items.filter(i => i.severity === 'critical').length,
          high: response.items.filter(i => i.severity === 'high').length,
        });
      } catch (error) {
        console.error('Error fetching incidents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Government Accountability Database
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          Tracking and documenting government actions, violations, and patterns
          to ensure accountability and transparency.
        </p>
        <Link
          to="/incidents"
          className="inline-block bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
        >
          Browse Incidents
        </Link>
      </section>

      {/* Statistics */}
      {!loading && (
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-4xl font-bold text-primary-600 mb-2">{stats.total}</div>
            <div className="text-gray-600">Total Incidents</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-4xl font-bold text-red-600 mb-2">{stats.critical}</div>
            <div className="text-gray-600">Critical Severity</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-4xl font-bold text-orange-600 mb-2">{stats.high}</div>
            <div className="text-gray-600">High Severity</div>
          </div>
        </section>
      )}

      {/* Recent Incidents */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-900">Recent Incidents</h2>
          <Link
            to="/incidents"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            View All →
          </Link>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading...</div>
        ) : (
          <div className="space-y-4">
            {recentIncidents.map((incident) => (
              <Link
                key={incident.id}
                to={`/incidents/${incident.id}`}
                className="block bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xl font-semibold text-gray-900 flex-1">
                    {incident.title}
                  </h3>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      incident.severity === 'critical'
                        ? 'bg-red-100 text-red-800'
                        : incident.severity === 'high'
                        ? 'bg-orange-100 text-orange-800'
                        : incident.severity === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {incident.severity}
                  </span>
                </div>
                <p className="text-gray-600 mb-3">{incident.summary}</p>
                <div className="flex items-center text-sm text-gray-500 space-x-4">
                  <span>{new Date(incident.date_occurred).toLocaleDateString()}</span>
                  <span>•</span>
                  <span>{incident.geographic_scope}</span>
                  <span>•</span>
                  <span>{incident.source_count} sources</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default HomePage;
