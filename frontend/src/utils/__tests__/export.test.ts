import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { exportIncidentsCSV, exportIncidentsJSON, exportAnalyticsCSV, buildExportQueryString } from '../export';
import type { IncidentFilters } from '../../types';

describe('buildExportQueryString', () => {
  it('builds empty query string with no filters', () => {
    const result = buildExportQueryString({});
    expect(result).toBe('');
  });

  it('builds query string with single filter', () => {
    const filters: IncidentFilters = {
      severity: 'high',
    };
    const result = buildExportQueryString(filters);
    expect(result).toBe('severity=high');
  });

  it('builds query string with multiple filters', () => {
    const filters: IncidentFilters = {
      severity: 'high',
      location_state: 'CA',
      search: 'incident',
    };
    const result = buildExportQueryString(filters);
    expect(result).toContain('severity=high');
    expect(result).toContain('location_state=CA');
    expect(result).toContain('search=incident');
  });

  it('includes date filters', () => {
    const filters: IncidentFilters = {
      date_from: '2024-01-01',
      date_to: '2024-12-31',
    };
    const result = buildExportQueryString(filters);
    expect(result).toContain('date_from=2024-01-01');
    expect(result).toContain('date_to=2024-12-31');
  });

  it('includes limit parameter', () => {
    const filters: IncidentFilters = {
      limit: 5000,
    };
    const result = buildExportQueryString(filters);
    expect(result).toContain('limit=5000');
  });

  it('properly encodes special characters', () => {
    const filters: IncidentFilters = {
      search: 'test & special',
    };
    const result = buildExportQueryString(filters);
    expect(result).toContain('test');
    expect(result).toContain('special');
  });
});

describe('exportIncidentsCSV', () => {
  let originalCreateElement: typeof document.createElement;
  let mockLink: Partial<HTMLAnchorElement>;

  beforeEach(() => {
    // Mock document.createElement for anchor element
    mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
    };

    originalCreateElement = document.createElement;
    document.createElement = vi.fn((tagName: string) => {
      if (tagName === 'a') {
        return mockLink as HTMLAnchorElement;
      }
      return originalCreateElement.call(document, tagName);
    });

    // Mock document.body methods
    document.body.appendChild = vi.fn();
    document.body.removeChild = vi.fn();
  });

  afterEach(() => {
    document.createElement = originalCreateElement;
    vi.clearAllMocks();
  });

  it('creates download link with correct URL', () => {
    const filters: IncidentFilters = {
      severity: 'high',
    };

    exportIncidentsCSV(filters);

    expect(mockLink.href).toContain('/api/export/incidents/csv');
    expect(mockLink.href).toContain('severity=high');
    expect(mockLink.download).toBe('incidents_export.csv');
  });

  it('triggers download', () => {
    exportIncidentsCSV();

    expect(mockLink.click).toHaveBeenCalled();
    expect(document.body.appendChild).toHaveBeenCalledWith(mockLink);
    expect(document.body.removeChild).toHaveBeenCalledWith(mockLink);
  });

  it('uses correct API URL from environment', () => {
    // Test with default URL
    exportIncidentsCSV();

    expect(mockLink.href).toContain('http://localhost:8000/api/export/incidents/csv');
  });

  it('handles empty filters', () => {
    exportIncidentsCSV({});

    expect(mockLink.href).toContain('/api/export/incidents/csv');
    expect(mockLink.click).toHaveBeenCalled();
  });

  it('includes all filter types', () => {
    const filters: IncidentFilters = {
      category_id: 'cat1',
      severity: 'critical',
      verification_status: 'documented',
      geographic_scope: 'federal',
      location_state: 'NY',
      date_from: '2024-01-01',
      date_to: '2024-12-31',
      search: 'test',
      limit: 1000,
    };

    exportIncidentsCSV(filters);

    expect(mockLink.href).toContain('category_id=cat1');
    expect(mockLink.href).toContain('severity=critical');
    expect(mockLink.href).toContain('verification_status=documented');
    expect(mockLink.href).toContain('geographic_scope=federal');
    expect(mockLink.href).toContain('location_state=NY');
    expect(mockLink.href).toContain('date_from=2024-01-01');
    expect(mockLink.href).toContain('date_to=2024-12-31');
    expect(mockLink.href).toContain('search=test');
    expect(mockLink.href).toContain('limit=1000');
  });
});

describe('exportIncidentsJSON', () => {
  let originalCreateElement: typeof document.createElement;
  let mockLink: Partial<HTMLAnchorElement>;

  beforeEach(() => {
    mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
    };

    originalCreateElement = document.createElement;
    document.createElement = vi.fn((tagName: string) => {
      if (tagName === 'a') {
        return mockLink as HTMLAnchorElement;
      }
      return originalCreateElement.call(document, tagName);
    });

    document.body.appendChild = vi.fn();
    document.body.removeChild = vi.fn();
  });

  afterEach(() => {
    document.createElement = originalCreateElement;
    vi.clearAllMocks();
  });

  it('creates download link with correct URL and filename', () => {
    exportIncidentsJSON();

    expect(mockLink.href).toContain('/api/export/incidents/json');
    expect(mockLink.download).toBe('incidents_export.json');
  });

  it('includes filters in URL', () => {
    const filters: IncidentFilters = {
      severity: 'high',
      location_state: 'CA',
    };

    exportIncidentsJSON(filters);

    expect(mockLink.href).toContain('severity=high');
    expect(mockLink.href).toContain('location_state=CA');
  });

  it('triggers download', () => {
    exportIncidentsJSON();

    expect(mockLink.click).toHaveBeenCalled();
    expect(document.body.appendChild).toHaveBeenCalledWith(mockLink);
    expect(document.body.removeChild).toHaveBeenCalledWith(mockLink);
  });
});

describe('exportAnalyticsCSV', () => {
  let originalCreateElement: typeof document.createElement;
  let mockLink: Partial<HTMLAnchorElement>;

  beforeEach(() => {
    mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
    };

    originalCreateElement = document.createElement;
    document.createElement = vi.fn((tagName: string) => {
      if (tagName === 'a') {
        return mockLink as HTMLAnchorElement;
      }
      return originalCreateElement.call(document, tagName);
    });

    document.body.appendChild = vi.fn();
    document.body.removeChild = vi.fn();
  });

  afterEach(() => {
    document.createElement = originalCreateElement;
    vi.clearAllMocks();
  });

  it('creates download link with correct URL and filename', () => {
    exportAnalyticsCSV();

    expect(mockLink.href).toContain('/api/export/analytics/csv');
    expect(mockLink.download).toBe('analytics_export.csv');
  });

  it('does not include query parameters', () => {
    exportAnalyticsCSV();

    // Analytics export doesn't take filters, so no ? should be in URL
    const url = mockLink.href || '';
    const hasQueryString = url.includes('?');
    expect(hasQueryString).toBe(false);
  });

  it('triggers download', () => {
    exportAnalyticsCSV();

    expect(mockLink.click).toHaveBeenCalled();
    expect(document.body.appendChild).toHaveBeenCalledWith(mockLink);
    expect(document.body.removeChild).toHaveBeenCalledWith(mockLink);
  });
});

describe('Export Integration', () => {
  it('all export functions use consistent patterns', () => {
    const mockLink: Partial<HTMLAnchorElement> = {
      href: '',
      download: '',
      click: vi.fn(),
    };

    const originalCreateElement = document.createElement;
    document.createElement = vi.fn(() => mockLink as HTMLAnchorElement);
    document.body.appendChild = vi.fn();
    document.body.removeChild = vi.fn();

    // Test all export functions
    exportIncidentsCSV();
    expect(mockLink.download).toBe('incidents_export.csv');

    exportIncidentsJSON();
    expect(mockLink.download).toBe('incidents_export.json');

    exportAnalyticsCSV();
    expect(mockLink.download).toBe('analytics_export.csv');

    // All should have called click
    expect(mockLink.click).toHaveBeenCalledTimes(3);

    document.createElement = originalCreateElement;
  });
});
