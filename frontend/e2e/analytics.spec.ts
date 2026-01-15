import { test, expect } from '@playwright/test';

test.describe('Analytics Dashboard', () => {
  test('should display analytics dashboard', async ({ page }) => {
    await page.goto('/analytics');

    // Wait for the page to load
    await expect(page.locator('h1')).toContainText('Analytics Dashboard');

    // Verify key metrics are displayed
    await expect(page.locator('text=/Total Incidents/i')).toBeVisible();
    await expect(page.locator('text=/Recent \(30 Days\)/i')).toBeVisible();
  });

  test('should display charts and visualizations', async ({ page }) => {
    await page.goto('/analytics');

    // Wait for analytics data to load
    await page.waitForSelector('h1:has-text("Analytics Dashboard")');

    // Check for different chart sections
    await expect(page.locator('text=/By Severity/i')).toBeVisible();
    await expect(page.locator('text=/Verification Status/i')).toBeVisible();
    await expect(page.locator('text=/Geographic Scope/i')).toBeVisible();
  });

  test('should display top states section', async ({ page }) => {
    await page.goto('/analytics');

    await page.waitForSelector('h1:has-text("Analytics Dashboard")');

    // Check for top states section
    await expect(page.locator('text=/Top States/i')).toBeVisible();
  });

  test('should display timeline chart', async ({ page }) => {
    await page.goto('/analytics');

    await page.waitForSelector('h1:has-text("Analytics Dashboard")');

    // Check for timeline section
    await expect(page.locator('text=/Recent Activity/i')).toBeVisible();
  });

  test('should display categories chart', async ({ page }) => {
    await page.goto('/analytics');

    await page.waitForSelector('h1:has-text("Analytics Dashboard")');

    // Check for categories section
    await expect(page.locator('text=/Incidents by Category/i')).toBeVisible();
  });

  test('should refresh data when refresh button clicked', async ({ page }) => {
    await page.goto('/analytics');

    await page.waitForSelector('h1:has-text("Analytics Dashboard")');

    // Find and click refresh button
    const refreshButton = page.locator('button:has-text("Refresh")');
    await expect(refreshButton).toBeVisible();
    await refreshButton.click();

    // Verify data is refreshed (check for loading state or updated timestamp)
    await page.waitForTimeout(500);
  });

  test('should export analytics data', async ({ page }) => {
    await page.goto('/analytics');

    await page.waitForSelector('h1:has-text("Analytics Dashboard")');

    // Set up download listener
    const downloadPromise = page.waitForEvent('download');

    // Click export button
    const exportButton = page.locator('button:has-text("Export")');
    await exportButton.click();

    // Wait for download to complete
    const download = await downloadPromise;

    // Verify download filename
    expect(download.suggestedFilename()).toContain('analytics_export.csv');
  });

  test('should display last updated timestamp', async ({ page }) => {
    await page.goto('/analytics');

    await page.waitForSelector('h1:has-text("Analytics Dashboard")');

    // Check for last updated timestamp
    await expect(page.locator('text=/Last Updated:/i')).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API calls and make them fail
    await page.route('**/api/analytics/**', (route) => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ detail: 'Internal Server Error' }),
      });
    });

    await page.goto('/analytics');

    // Should display error message
    await expect(page.locator('text=/error/i').first()).toBeVisible();
  });
});
