import { test, expect } from '@playwright/test';

test.describe('Search and Filter', () => {
  test('should perform text search', async ({ page }) => {
    await page.goto('/');

    // Wait for page to load
    await page.waitForSelector('[data-testid="incident-list"]');

    // Find search input
    const searchInput = page.locator('input[placeholder*="Search"]');
    await expect(searchInput).toBeVisible();

    // Enter search term
    await searchInput.fill('corruption');
    await searchInput.press('Enter');

    // Wait for results to update
    await page.waitForTimeout(500);

    // Verify URL contains search parameter
    await expect(page).toHaveURL(/search=corruption/);
  });

  test('should filter by severity', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Find severity filter
    const severityFilter = page.locator('select[name="severity"]');
    await expect(severityFilter).toBeVisible();

    // Select a severity
    await severityFilter.selectOption('high');

    // Wait for results to update
    await page.waitForTimeout(500);

    // Verify URL contains severity parameter
    await expect(page).toHaveURL(/severity=high/);
  });

  test('should filter by verification status', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Find verification status filter
    const statusFilter = page.locator('select[name="verification_status"]');
    await expect(statusFilter).toBeVisible();

    // Select a status
    await statusFilter.selectOption('documented');

    // Wait for results to update
    await page.waitForTimeout(500);

    // Verify URL contains status parameter
    await expect(page).toHaveURL(/verification_status=documented/);
  });

  test('should filter by geographic scope', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Find geographic scope filter
    const scopeFilter = page.locator('select[name="geographic_scope"]');
    await expect(scopeFilter).toBeVisible();

    // Select a scope
    await scopeFilter.selectOption('federal');

    // Wait for results to update
    await page.waitForTimeout(500);

    // Verify URL contains scope parameter
    await expect(page).toHaveURL(/geographic_scope=federal/);
  });

  test('should filter by state', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Find state filter
    const stateFilter = page.locator('select[name="location_state"]');
    await expect(stateFilter).toBeVisible();

    // Select a state
    await stateFilter.selectOption('CA');

    // Wait for results to update
    await page.waitForTimeout(500);

    // Verify URL contains state parameter
    await expect(page).toHaveURL(/location_state=CA/);
  });

  test('should filter by date range', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Find date inputs
    const dateFromInput = page.locator('input[name="date_from"]');
    const dateToInput = page.locator('input[name="date_to"]');

    await expect(dateFromInput).toBeVisible();
    await expect(dateToInput).toBeVisible();

    // Set date range
    await dateFromInput.fill('2024-01-01');
    await dateToInput.fill('2024-12-31');
    await dateFromInput.press('Enter');

    // Wait for results to update
    await page.waitForTimeout(500);

    // Verify URL contains date parameters
    await expect(page).toHaveURL(/date_from=2024-01-01/);
    await expect(page).toHaveURL(/date_to=2024-12-31/);
  });

  test('should combine multiple filters', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Apply multiple filters
    await page.locator('select[name="severity"]').selectOption('high');
    await page.locator('select[name="verification_status"]').selectOption('documented');
    await page.locator('input[placeholder*="Search"]').fill('fraud');
    await page.locator('input[placeholder*="Search"]').press('Enter');

    // Wait for results to update
    await page.waitForTimeout(500);

    // Verify URL contains all parameters
    await expect(page).toHaveURL(/severity=high/);
    await expect(page).toHaveURL(/verification_status=documented/);
    await expect(page).toHaveURL(/search=fraud/);
  });

  test('should clear filters', async ({ page }) => {
    await page.goto('/?severity=high&search=corruption');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Find and click clear filters button
    const clearButton = page.locator('button:has-text("Clear")');
    await expect(clearButton).toBeVisible();
    await clearButton.click();

    // Wait for results to update
    await page.waitForTimeout(500);

    // Verify URL has no filter parameters
    await expect(page).toHaveURL('/');
  });

  test('should persist filters across navigation', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="incident-list"]');

    // Apply filter
    await page.locator('select[name="severity"]').selectOption('high');

    // Wait for results to update
    await page.waitForTimeout(500);

    // Navigate to analytics and back
    await page.click('a[href="/analytics"]');
    await page.waitForSelector('h1:has-text("Analytics")');
    await page.goBack();

    // Verify filter is still applied
    await expect(page).toHaveURL(/severity=high/);
    await expect(page.locator('select[name="severity"]')).toHaveValue('high');
  });
});
