/**
 * Utility functions for exporting data
 */

import type { IncidentFilters } from '../types';

/**
 * Build query string from filters
 */
export function buildExportQueryString(filters: IncidentFilters): string {
  const params = new URLSearchParams();

  if (filters.category_id) params.set('category_id', filters.category_id);
  if (filters.actor_id) params.set('actor_id', filters.actor_id);
  if (filters.severity) params.set('severity', filters.severity);
  if (filters.verification_status) params.set('verification_status', filters.verification_status);
  if (filters.geographic_scope) params.set('geographic_scope', filters.geographic_scope);
  if (filters.location_state) params.set('location_state', filters.location_state);
  if (filters.date_from) params.set('date_from', filters.date_from);
  if (filters.date_to) params.set('date_to', filters.date_to);
  if (filters.search) params.set('search', filters.search);
  if (filters.limit) params.set('limit', filters.limit.toString());

  return params.toString();
}

/**
 * Export incidents to CSV
 */
export function exportIncidentsCSV(filters: IncidentFilters = {}): void {
  const queryString = buildExportQueryString(filters);
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const url = `${baseUrl}/api/export/incidents/csv?${queryString}`;

  // Create temporary link and trigger download
  const link = document.createElement('a');
  link.href = url;
  link.download = 'incidents_export.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Export incidents to JSON
 */
export function exportIncidentsJSON(filters: IncidentFilters = {}): void {
  const queryString = buildExportQueryString(filters);
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const url = `${baseUrl}/api/export/incidents/json?${queryString}`;

  // Create temporary link and trigger download
  const link = document.createElement('a');
  link.href = url;
  link.download = 'incidents_export.json';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Export analytics to CSV
 */
export function exportAnalyticsCSV(): void {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const url = `${baseUrl}/api/export/analytics/csv`;

  // Create temporary link and trigger download
  const link = document.createElement('a');
  link.href = url;
  link.download = 'analytics_export.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
