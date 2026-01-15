import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { format } from 'date-fns';
import { incidentsApi } from '../services/api';
import type { IncidentDetail } from '../types';

const IncidentDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIncident = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const data = await incidentsApi.get(id);
        setIncident(data);
      } catch (err) {
        console.error('Error fetching incident:', err);
        setError('Failed to load incident details');
      } finally {
        setLoading(false);
      }
    };

    fetchIncident();
  }, [id]);

  if (loading) {
    return (
      <div className="text-center py-12 text-gray-500">Loading incident details...</div>
    );
  }

  if (error || !incident) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error || 'Incident not found'}</p>
        <Link to="/incidents" className="text-primary-600 hover:text-primary-700 font-medium">
          ← Back to incidents
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Back Link */}
      <Link to="/incidents" className="text-primary-600 hover:text-primary-700 font-medium">
        ← Back to incidents
      </Link>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex flex-wrap gap-3 mb-4">
          <span
            className={`px-4 py-2 rounded-full text-sm font-medium ${
              incident.severity === 'critical'
                ? 'bg-red-100 text-red-800'
                : incident.severity === 'high'
                ? 'bg-orange-100 text-orange-800'
                : incident.severity === 'medium'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {incident.severity.toUpperCase()}
          </span>
          <span className="px-4 py-2 rounded-full text-sm font-medium bg-blue-100 text-blue-800 capitalize">
            {incident.verification_status}
          </span>
          <span className="px-4 py-2 rounded-full text-sm font-medium bg-purple-100 text-purple-800 capitalize">
            {incident.geographic_scope}
          </span>
        </div>

        <h1 className="text-4xl font-bold text-gray-900 mb-4">{incident.title}</h1>

        <div className="flex flex-wrap items-center text-gray-600 gap-4 mb-6">
          <span className="font-medium">
            {format(new Date(incident.date_occurred), 'MMMM d, yyyy')}
          </span>
          {incident.location_city && incident.location_state && (
            <>
              <span>•</span>
              <span>
                {incident.location_city}, {incident.location_state}
              </span>
            </>
          )}
        </div>

        <p className="text-lg text-gray-700 mb-4">{incident.summary}</p>

        {incident.detailed_description && (
          <div className="prose max-w-none">
            <p className="text-gray-600">{incident.detailed_description}</p>
          </div>
        )}
      </div>

      {/* Actors */}
      {incident.actors && incident.actors.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Actors Involved</h2>
          <div className="space-y-3">
            {incident.actors.map((ia, index) => (
              <div key={index} className="flex items-start border-l-4 border-primary-500 pl-4 py-2">
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">{ia.actor.name}</div>
                  <div className="text-sm text-gray-600 capitalize">
                    Role: <span className="font-medium">{ia.role}</span>
                  </div>
                  <div className="text-sm text-gray-500 capitalize">
                    Type: {ia.actor.actor_type}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Targets */}
      {incident.targets && incident.targets.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Affected Groups</h2>
          <div className="flex flex-wrap gap-3">
            {incident.targets.map((target) => (
              <div
                key={target.id}
                className="px-4 py-2 bg-orange-100 text-orange-800 rounded-lg font-medium"
              >
                {target.name}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Legal Frameworks */}
      {incident.legal_frameworks && incident.legal_frameworks.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Legal Framework Violations</h2>
          <div className="space-y-4">
            {incident.legal_frameworks.map((ilf, index) => (
              <div key={index} className="border-l-4 border-red-500 pl-4 py-2">
                <div className="font-semibold text-gray-900">{ilf.legal_framework.name}</div>
                <div className="text-sm text-gray-600">
                  {ilf.legal_framework.citation && (
                    <span className="italic">{ilf.legal_framework.citation}</span>
                  )}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {ilf.legal_framework.description}
                </div>
                <div className="text-sm font-medium text-red-600 mt-1 capitalize">
                  Violation Status: {ilf.violation_type}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Patterns */}
      {incident.patterns && incident.patterns.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Systematic Patterns</h2>
          <div className="space-y-3">
            {incident.patterns.map((pattern) => (
              <div key={pattern.id} className="border-l-4 border-purple-500 pl-4 py-2">
                <div className="font-semibold text-gray-900">{pattern.name}</div>
                {pattern.description && (
                  <div className="text-sm text-gray-600 mt-1">{pattern.description}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sources */}
      {incident.sources && incident.sources.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Sources</h2>
          <div className="space-y-4">
            {incident.sources.map((source) => (
              <div key={source.id} className="border-l-4 border-green-500 pl-4 py-2">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900">{source.title}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      {source.author && <span>By {source.author}</span>}
                      {source.publication_date && (
                        <span className="ml-2">
                          • {format(new Date(source.publication_date), 'MMM d, yyyy')}
                        </span>
                      )}
                    </div>
                    {source.url && (
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700 text-sm mt-1 inline-block"
                      >
                        View source →
                      </a>
                    )}
                  </div>
                  <div className="ml-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        source.reliability === 'primary'
                          ? 'bg-green-100 text-green-800'
                          : source.reliability === 'secondary'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {source.reliability}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default IncidentDetailPage;
