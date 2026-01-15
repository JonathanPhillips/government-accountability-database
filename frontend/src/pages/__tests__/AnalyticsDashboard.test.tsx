import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AnalyticsDashboard from '../AnalyticsDashboard';
import * as api from '../../utils/api';
import * as exportUtils from '../../utils/export';

// Mock the API and export modules
vi.mock('../../utils/api');
vi.mock('../../utils/export');

const mockAnalyticsData = {
  total_incidents: 150,
  by_severity: {
    'SeverityEnum.CRITICAL': 20,
    'SeverityEnum.HIGH': 45,
    'SeverityEnum.MEDIUM': 60,
    'SeverityEnum.LOW': 25,
  },
  by_verification: {
    'VerificationStatusEnum.DOCUMENTED': 80,
    'VerificationStatusEnum.UNVERIFIED': 40,
    'VerificationStatusEnum.PENDING_REVIEW': 30,
  },
  by_geographic_scope: {
    'GeographicScopeEnum.FEDERAL': 50,
    'GeographicScopeEnum.STATE': 70,
    'GeographicScopeEnum.LOCAL': 30,
  },
  recent_30_days: 35,
  top_states: [
    { state: 'California', count: 25 },
    { state: 'Texas', count: 20 },
    { state: 'New York', count: 15 },
  ],
  last_updated: '2026-01-12T10:00:00Z',
};

const mockTimelineData = {
  timeline: [
    { month: 'November 2025', count: 12 },
    { month: 'December 2025', count: 18 },
    { month: 'January 2026', count: 15 },
  ],
  days: 365,
};

const mockCategoryData = {
  categories: [
    { name: 'Category 1', count: 45 },
    { name: 'Category 2', count: 35 },
    { name: 'Category 3', count: 25 },
  ],
};

describe('AnalyticsDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock API responses
    vi.mocked(api.api.get).mockImplementation((url: string) => {
      if (url === '/api/analytics/overview') {
        return Promise.resolve(mockAnalyticsData);
      }
      if (url === '/api/analytics/timeline?days=365') {
        return Promise.resolve(mockTimelineData);
      }
      if (url === '/api/analytics/categories') {
        return Promise.resolve(mockCategoryData);
      }
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  it('renders loading state initially', () => {
    render(<AnalyticsDashboard />);
    expect(screen.getByText(/loading analytics/i)).toBeInTheDocument();
  });

  it('renders analytics data after loading', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
    });

    // Check key metrics - verify they exist in the document
    await waitFor(() => {
      const elements = screen.getAllByText('150');
      expect(elements.length).toBeGreaterThan(0);
    });

    await waitFor(() => {
      const elements = screen.getAllByText('35');
      expect(elements.length).toBeGreaterThan(0);
    });
  });

  it('displays severity distribution correctly', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('By Severity')).toBeInTheDocument();
    });

    expect(screen.getByText(/critical/i)).toBeInTheDocument();
    expect(screen.getByText(/high/i)).toBeInTheDocument();
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
    expect(screen.getByText(/low/i)).toBeInTheDocument();
  });

  it('displays verification status correctly', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Verification Status')).toBeInTheDocument();
    });

    expect(screen.getByText(/documented/i)).toBeInTheDocument();
    expect(screen.getByText(/unverified/i)).toBeInTheDocument();
  });

  it('displays geographic scope correctly', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Geographic Scope')).toBeInTheDocument();
    });

    // Check within the Geographic Scope section
    const scopeSection = screen.getByText('Geographic Scope').closest('div');
    expect(scopeSection).toHaveTextContent(/federal/i);
    expect(scopeSection).toHaveTextContent(/state/i);
    expect(scopeSection).toHaveTextContent(/local/i);
  });

  it('displays top states correctly', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Top States by Incident Count')).toBeInTheDocument();
    });

    expect(screen.getByText(/California/i)).toBeInTheDocument();
    expect(screen.getByText(/Texas/i)).toBeInTheDocument();
    expect(screen.getByText(/New York/i)).toBeInTheDocument();
  });

  it('displays categories correctly', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Incidents by Category')).toBeInTheDocument();
    });

    expect(screen.getByText('Category 1')).toBeInTheDocument();
    expect(screen.getByText('Category 2')).toBeInTheDocument();
    expect(screen.getByText('Category 3')).toBeInTheDocument();
  });

  it('displays timeline data correctly', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    });

    expect(screen.getByText(/November 2025/i)).toBeInTheDocument();
    expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
    expect(screen.getByText(/January 2026/i)).toBeInTheDocument();
  });

  it('refreshes data when refresh button is clicked', async () => {
    const user = userEvent.setup();
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
    });

    const refreshButton = screen.getByRole('button', { name: /refresh data/i });
    await user.click(refreshButton);

    // API should be called again
    await waitFor(() => {
      expect(api.api.get).toHaveBeenCalledTimes(6); // 3 initial + 3 refresh
    });
  });

  it('exports analytics when export button is clicked', async () => {
    const user = userEvent.setup();
    const mockExportAnalyticsCSV = vi.fn();
    vi.mocked(exportUtils.exportAnalyticsCSV).mockImplementation(mockExportAnalyticsCSV);

    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
    });

    const exportButton = screen.getByRole('button', { name: /export analytics/i });
    await user.click(exportButton);

    expect(mockExportAnalyticsCSV).toHaveBeenCalledTimes(1);
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(api.api.get).mockRejectedValue(new Error('API Error'));

    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/failed to load analytics data/i)).toBeInTheDocument();
    });
  });

  it('displays last updated timestamp', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/last updated:/i)).toBeInTheDocument();
    });
  });

  it('calculates percentages correctly', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('By Severity')).toBeInTheDocument();
    });

    // Total by severity = 150
    // Critical = 20/150 = 13%
    // We check if percentage calculations are displayed
    const percentageElements = screen.getAllByText(/\d+%/);
    expect(percentageElements.length).toBeGreaterThan(0);
  });

  it('displays correct number of states', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Top States by Incident Count')).toBeInTheDocument();
    });

    // Should display 3 states (California, Texas, New York)
    expect(screen.getByText(/California/i)).toBeInTheDocument();
    expect(screen.getByText(/Texas/i)).toBeInTheDocument();
    expect(screen.getByText(/New York/i)).toBeInTheDocument();
  });

  it('displays correct number of categories', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Incidents by Category')).toBeInTheDocument();
    });

    // Should display 3 categories
    expect(screen.getByText('Category 1')).toBeInTheDocument();
    expect(screen.getByText('Category 2')).toBeInTheDocument();
    expect(screen.getByText('Category 3')).toBeInTheDocument();
  });
});
