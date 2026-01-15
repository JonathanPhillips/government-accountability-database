import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should display main dashboard with incident list', async ({ page }) => {
    await page.goto('/');

    // Wait for the page to load
    await expect(page.locator('h1')).toContainText('Government Accountability Database');

    // Check that incidents are displayed
    await expect(page.locator('[data-testid="incident-list"]')).toBeVisible();
  });

  test('should navigate to analytics page', async ({ page }) => {
    await page.goto('/');

    // Click on Analytics link
    await page.click('a[href="/analytics"]');

    // Verify we're on the analytics page
    await expect(page).toHaveURL('/analytics');
    await expect(page.locator('h1')).toContainText('Analytics Dashboard');
  });

  test('should display loading state initially', async ({ page }) => {
    await page.goto('/');

    // Should see loading indicator
    await expect(page.locator('text=/loading/i').first()).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API call and make it fail
    await page.route('**/api/incidents**', (route) => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ detail: 'Internal Server Error' }),
      });
    });

    await page.goto('/');

    // Should display error message
    await expect(page.locator('text=/error/i').first()).toBeVisible();
  });

  test('should paginate incident list', async ({ page }) => {
    await page.goto('/');

    // Wait for incidents to load
    await page.waitForSelector('[data-testid="incident-list"]');

    // Check if pagination controls are visible
    const paginationControls = page.locator('[data-testid="pagination"]');
    await expect(paginationControls).toBeVisible();

    // Click next page button
    await page.click('button:has-text("Next")');

    // Verify page changed (URL or content)
    await page.waitForTimeout(500);
  });

  test('should navigate to incident details', async ({ page }) => {
    await page.goto('/');

    // Wait for incidents to load
    await page.waitForSelector('[data-testid="incident-list"]');

    // Click on first incident
    const firstIncident = page.locator('[data-testid="incident-card"]').first();
    await firstIncident.click();

    // Verify we're on the incident details page
    await expect(page).toHaveURL(/\/incident\/.+/);
  });
});
