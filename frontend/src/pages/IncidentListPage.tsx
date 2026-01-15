import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { incidentsApi, categoriesApi } from '../services/api';
import type { IncidentListItem, Category, IncidentFilters, SeverityType } from '../types';
import { exportIncidentsCSV, exportIncidentsJSON } from '../utils/export';

const IncidentListPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [incidents, setIncidents] = useState<IncidentListItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  // Filter state
  const [filters, setFilters] = useState<IncidentFilters>({
    search: searchParams.get('search') || '',
    category_id: searchParams.get('category_id') || undefined,
    severity: (searchParams.get('severity') as SeverityType) || undefined,
    verification_status: searchParams.get('verification_status') || undefined,
    geographic_scope: searchParams.get('geographic_scope') || undefined,
    location_state: searchParams.get('location_state') || undefined,
    date_from: searchParams.get('date_from') || undefined,
    date_to: searchParams.get('date_to') || undefined,
    skip: 0,
    limit: 20,
  });

  const [sortBy, setSortBy] = useState<'date' | 'severity' | 'recent'>('date');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchIncidents();
  }, [filters]);

  const fetchCategories = async () => {
    try {
      const response = await categoriesApi.list();
      setCategories(response.items);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const response = await incidentsApi.list(filters);
      setIncidents(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Error fetching incidents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: keyof IncidentFilters, value: any) => {
    const newFilters = { ...filters, [key]: value, skip: 0 };
    setFilters(newFilters);

    // Update URL params
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v !== undefined && v !== '' && v !== 0) {
        params.set(k, v.toString());
      }
    });
    setSearchParams(params);
  };

  const clearFilters = () => {
    setFilters({ skip: 0, limit: 20 });
    setSearchParams({});
  };

  const hasActiveFilters = () => {
    return filters.search || filters.category_id || filters.severity ||
           filters.verification_status || filters.geographic_scope ||
           filters.location_state || filters.date_from || filters.date_to;
  };

  const loadMore = () => {
    setFilters({ ...filters, skip: (filters.skip || 0) + (filters.limit || 20) });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-4xl font-bold text-gray-900">Incidents</h1>
        <div className="flex items-center gap-4">
          <div className="text-gray-600">{total} incidents found</div>

          {/* Export Dropdown */}
          <div className="relative group">
            <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm font-medium flex items-center gap-2">
              Export
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
              <button
                onClick={() => exportIncidentsCSV(filters)}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 text-sm font-medium text-gray-700 flex items-center gap-2 rounded-t-lg"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export as CSV
              </button>
              <button
                onClick={() => exportIncidentsJSON(filters)}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 text-sm font-medium text-gray-700 flex items-center gap-2 rounded-b-lg border-t border-gray-100"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export as JSON
              </button>
            </div>
          </div>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            <option value="date">Sort by Date</option>
            <option value="severity">Sort by Severity</option>
            <option value="recent">Most Recent</option>
          </select>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Search & Filters</h2>
          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className="text-primary-600 hover:text-primary-700 font-medium text-sm"
          >
            {showAdvancedFilters ? 'Hide' : 'Show'} Advanced Filters
          </button>
        </div>

        <div className="space-y-4">
          {/* Basic Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <input
                type="text"
                value={filters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="Search title, description..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                value={filters.category_id || ''}
                onChange={(e) => handleFilterChange('category_id', e.target.value || undefined)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Severity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Severity
              </label>
              <select
                value={filters.severity || ''}
                onChange={(e) => handleFilterChange('severity', e.target.value as SeverityType || undefined)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>

          {/* Advanced Filters */}
          {showAdvancedFilters && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
              {/* Verification Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Verification Status
                </label>
                <select
                  value={filters.verification_status || ''}
                  onChange={(e) => handleFilterChange('verification_status', e.target.value || undefined)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">All Statuses</option>
                  <option value="verified">Verified</option>
                  <option value="unverified">Unverified</option>
                  <option value="disputed">Disputed</option>
                  <option value="debunked">Debunked</option>
                </select>
              </div>

              {/* Geographic Scope */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Geographic Scope
                </label>
                <select
                  value={filters.geographic_scope || ''}
                  onChange={(e) => handleFilterChange('geographic_scope', e.target.value || undefined)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">All Scopes</option>
                  <option value="local">Local</option>
                  <option value="state">State</option>
                  <option value="regional">Regional</option>
                  <option value="national">National</option>
                  <option value="international">International</option>
                </select>
              </div>

              {/* State */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  State
                </label>
                <input
                  type="text"
                  value={filters.location_state || ''}
                  onChange={(e) => handleFilterChange('location_state', e.target.value || undefined)}
                  placeholder="e.g., CA, NY, TX"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              {/* Date From */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date From
                </label>
                <input
                  type="date"
                  value={filters.date_from || ''}
                  onChange={(e) => handleFilterChange('date_from', e.target.value || undefined)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              {/* Date To */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date To
                </label>
                <input
                  type="date"
                  value={filters.date_to || ''}
                  onChange={(e) => handleFilterChange('date_to', e.target.value || undefined)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          )}

          {/* Clear Filters Button */}
          {hasActiveFilters() && (
            <div className="pt-4 border-t border-gray-200">
              <button
                onClick={clearFilters}
                className="text-primary-600 hover:text-primary-700 font-medium text-sm"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters() && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">Active Filters:</span>
            <button
              onClick={clearFilters}
              className="text-blue-700 hover:text-blue-900 text-sm font-medium"
            >
              Clear All
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {filters.search && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                Search: "{filters.search}"
              </span>
            )}
            {filters.severity && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                Severity: {filters.severity}
              </span>
            )}
            {filters.verification_status && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                Status: {filters.verification_status}
              </span>
            )}
            {filters.geographic_scope && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                Scope: {filters.geographic_scope}
              </span>
            )}
            {filters.location_state && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                State: {filters.location_state}
              </span>
            )}
            {(filters.date_from || filters.date_to) && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                Date: {filters.date_from || '...'} to {filters.date_to || '...'}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Incidents List */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading incidents...</div>
      ) : incidents.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No incidents found</p>
          {hasActiveFilters() && (
            <button
              onClick={clearFilters}
              className="mt-4 text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {incidents.map((incident) => (
              <Link
                key={incident.id}
                to={`/incidents/${incident.id}`}
                className="block bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-xl font-semibold text-gray-900 flex-1 mr-4">
                    {incident.title}
                  </h3>
                  <div className="flex flex-col items-end space-y-2">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap ${
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
                    <span className="px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                      {incident.verification_status}
                    </span>
                  </div>
                </div>

                <p className="text-gray-600 mb-4">{incident.summary}</p>

                <div className="flex flex-wrap items-center text-sm text-gray-500 gap-4">
                  <span className="font-medium">
                    {new Date(incident.date_occurred).toLocaleDateString()}
                  </span>
                  <span>•</span>
                  <span className="capitalize">{incident.geographic_scope}</span>
                  {incident.location_state && (
                    <>
                      <span>•</span>
                      <span>
                        {incident.location_city && `${incident.location_city}, `}
                        {incident.location_state}
                      </span>
                    </>
                  )}
                  <span>•</span>
                  <span>{incident.source_count} sources</span>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {incidents.length < total && (
            <div className="text-center mt-8">
              <button
                onClick={loadMore}
                disabled={loading}
                className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Load More ({incidents.length} of {total})
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default IncidentListPage;
