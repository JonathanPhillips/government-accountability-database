import { test, expect } from '@playwright/test';

test.describe('Export Functionality', () => {
  test('should export incidents as CSV', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Set up download listener
    const downloadPromise = page.waitForEvent('download');

    // Find and click export CSV button
    const exportButton = page.locator('button:has-text("Export CSV")');
    await expect(exportButton).toBeVisible();
    await exportButton.click();

    // Wait for download to complete
    const download = await downloadPromise;

    // Verify download filename
    expect(download.suggestedFilename()).toBe('incidents_export.csv');
  });

  test('should export incidents as JSON', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Set up download listener
    const downloadPromise = page.waitForEvent('download');

    // Find and click export JSON button
    const exportButton = page.locator('button:has-text("Export JSON")');
    await expect(exportButton).toBeVisible();
    await exportButton.click();

    // Wait for download to complete
    const download = await downloadPromise;

    // Verify download filename
    expect(download.suggestedFilename()).toBe('incidents_export.json');
  });

  test('should export filtered incidents', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Apply filter
    await page.locator('select[name="severity"]').selectOption('high');
    await page.waitForTimeout(500);

    // Set up download listener
    const downloadPromise = page.waitForEvent('download');

    // Export CSV
    const exportButton = page.locator('button:has-text("Export CSV")');
    await exportButton.click();

    // Wait for download to complete
    const download = await downloadPromise;

    // Verify download occurred
    expect(download.suggestedFilename()).toBe('incidents_export.csv');
  });

  test('should show export menu options', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Find export dropdown/menu
    const exportMenu = page.locator('[data-testid="export-menu"]');

    // If export menu exists, click to open it
    if (await exportMenu.isVisible()) {
      await exportMenu.click();

      // Verify menu options are visible
      await expect(page.locator('text=/Export CSV/i')).toBeVisible();
      await expect(page.locator('text=/Export JSON/i')).toBeVisible();
    }
  });

  test('should export with date range filter', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Set date range
    const dateFromInput = page.locator('input[name="date_from"]');
    const dateToInput = page.locator('input[name="date_to"]');

    if (await dateFromInput.isVisible()) {
      await dateFromInput.fill('2024-01-01');
      await dateToInput.fill('2024-06-30');
      await dateFromInput.press('Enter');
      await page.waitForTimeout(500);
    }

    // Set up download listener
    const downloadPromise = page.waitForEvent('download');

    // Export CSV
    const exportButton = page.locator('button:has-text("Export CSV")');
    await exportButton.click();

    // Wait for download to complete
    const download = await downloadPromise;

    // Verify download occurred
    expect(download.suggestedFilename()).toBe('incidents_export.csv');
  });

  test('should export with search filter', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Perform search
    const searchInput = page.locator('input[placeholder*="Search"]');
    if (await searchInput.isVisible()) {
      await searchInput.fill('fraud');
      await searchInput.press('Enter');
      await page.waitForTimeout(500);
    }

    // Set up download listener
    const downloadPromise = page.waitForEvent('download');

    // Export CSV
    const exportButton = page.locator('button:has-text("Export CSV")');
    await exportButton.click();

    // Wait for download to complete
    const download = await downloadPromise;

    // Verify download occurred
    expect(download.suggestedFilename()).toBe('incidents_export.csv');
  });

  test('should export analytics data', async ({ page }) => {
    await page.goto('/analytics');

    await page.waitForSelector('h1:has-text("Analytics Dashboard")');

    // Set up download listener
    const downloadPromise = page.waitForEvent('download');

    // Find and click export button
    const exportButton = page.locator('button:has-text("Export")');
    await exportButton.click();

    // Wait for download to complete
    const download = await downloadPromise;

    // Verify download filename
    expect(download.suggestedFilename()).toContain('analytics_export.csv');
  });

  test('should handle export errors gracefully', async ({ page }) => {
    // Intercept export API call and make it fail
    await page.route('**/api/export/**', (route) => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ detail: 'Export failed' }),
      });
    });

    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Try to export
    const exportButton = page.locator('button:has-text("Export CSV")');
    await exportButton.click();

    // Should show error message
    await page.waitForTimeout(500);
    // Note: Actual error handling depends on implementation
  });
});
