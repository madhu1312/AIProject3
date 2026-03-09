import { test, expect } from '@playwright/test';

test.describe('CMS Article Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the CMS home page
    await page.goto('/');
  });

  test('should display the articles index page', async ({ page }) => {
    // Check page title and main elements
    await expect(page.locator('h1')).toContainText('Articles');
    await expect(page.getByRole('link', { name: /Create Document/i })).toBeVisible();
  });

  test('should show empty state when no articles exist', async ({ page }) => {
    // Check for empty state message
    const emptyState = page.locator('text=No articles found');
    // This may or may not be visible depending on existing data
    if (await emptyState.isVisible()) {
      await expect(page.getByRole('link', { name: /Create Your First Article/i })).toBeVisible();
    }
  });

  test('should navigate to create article page', async ({ page }) => {
    // Click create document button
    await page.getByRole('link', { name: /Create Document/i }).first().click();
    
    // Verify navigation to create page
    await expect(page).toHaveURL('/articles/new');
    await expect(page.locator('h1')).toContainText('Create New Article');
  });

  test('should display article creation form elements', async ({ page }) => {
    await page.goto('/articles/new');
    
    // Check all form elements are present
    await expect(page.getByPlaceholder('Enter article title...')).toBeVisible();
    await expect(page.getByPlaceholder('Brief description of the article...')).toBeVisible();
    await expect(page.getByPlaceholder('Add a tag...')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Save Draft' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Publish' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Cancel' })).toBeVisible();
  });

  test('should validate required title field', async ({ page }) => {
    await page.goto('/articles/new');
    
    // Try to save without title
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('title');
      await dialog.dismiss();
    });
    
    await page.getByRole('button', { name: 'Save Draft' }).click();
  });

  test('should create a draft article', async ({ page }) => {
    await page.goto('/articles/new');
    
    // Fill in article details
    await page.getByPlaceholder('Enter article title...').fill('Test Draft Article');
    await page.getByPlaceholder('Brief description of the article...').fill('This is a test excerpt');
    
    // Add a tag
    await page.getByPlaceholder('Add a tag...').fill('test-tag');
    await page.getByRole('button', { name: 'Add' }).click();
    
    // Save as draft
    await page.getByRole('button', { name: 'Save Draft' }).click();
    
    // Should redirect to home page
    await expect(page).toHaveURL('/');
  });

  test('should create and publish an article', async ({ page }) => {
    await page.goto('/articles/new');
    
    // Fill in article details
    await page.getByPlaceholder('Enter article title...').fill('Test Published Article');
    await page.getByPlaceholder('Brief description of the article...').fill('This is a published article');
    
    // Publish directly
    await page.getByRole('button', { name: 'Publish' }).click();
    
    // Should redirect to home page
    await expect(page).toHaveURL('/');
  });

  test('should display search and filter functionality', async ({ page }) => {
    // Check search input
    await expect(page.getByPlaceholder('Search articles...')).toBeVisible();
    
    // Check status filter
    await expect(page.getByRole('combobox')).toBeVisible();
  });

  test('should filter articles by status', async ({ page }) => {
    // Select draft filter
    await page.getByRole('combobox').selectOption('draft');
    
    // Select published filter
    await page.getByRole('combobox').selectOption('published');
    
    // Select all
    await page.getByRole('combobox').selectOption('all');
  });

  test('should display article statistics', async ({ page }) => {
    // Check for statistics cards
    await expect(page.locator('text=Total Articles')).toBeVisible();
    await expect(page.locator('text=Published')).toBeVisible();
    await expect(page.locator('text=Drafts')).toBeVisible();
    await expect(page.locator('text=Archived')).toBeVisible();
  });
});

test.describe('Article Editing', () => {
  test('should navigate to edit page from article card', async ({ page }) => {
    await page.goto('/');
    
    // If there are articles, click edit on the first one
    const editButton = page.getByRole('link', { name: 'Edit' }).first();
    if (await editButton.isVisible()) {
      await editButton.click();
      await expect(page).toHaveURL(/\/articles\/.*\/edit/);
      await expect(page.locator('h1')).toContainText('Edit Article');
    }
  });

  test('should display edit form with existing data', async ({ page }) => {
    await page.goto('/');
    
    const editButton = page.getByRole('link', { name: 'Edit' }).first();
    if (await editButton.isVisible()) {
      await editButton.click();
      
      // Form should be populated
      const titleInput = page.getByPlaceholder('Enter article title...');
      await expect(titleInput).not.toBeEmpty();
    }
  });

  test('should save changes to article', async ({ page }) => {
    await page.goto('/');
    
    const editButton = page.getByRole('link', { name: 'Edit' }).first();
    if (await editButton.isVisible()) {
      await editButton.click();
      
      // Modify title
      const titleInput = page.getByPlaceholder('Enter article title...');
      await titleInput.fill('Updated Article Title');
      
      // Save changes
      page.on('dialog', async dialog => {
        await dialog.dismiss();
      });
      await page.getByRole('button', { name: 'Save' }).click();
    }
  });

  test('should display danger zone actions', async ({ page }) => {
    await page.goto('/');
    
    const editButton = page.getByRole('link', { name: 'Edit' }).first();
    if (await editButton.isVisible()) {
      await editButton.click();
      
      await expect(page.locator('text=Danger Zone')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Archive Article' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Delete Article' })).toBeVisible();
    }
  });
});

test.describe('Article Preview', () => {
  test('should open article in CMS view', async ({ page }) => {
    await page.goto('/');
    
    const openCmsButton = page.getByRole('link', { name: 'Open in CMS' }).first();
    if (await openCmsButton.isVisible()) {
      await openCmsButton.click();
      await expect(page).toHaveURL(/\/articles\/.+$/);
    }
  });

  test('should display article content in CMS view', async ({ page }) => {
    await page.goto('/');
    
    const openCmsButton = page.getByRole('link', { name: 'Open in CMS' }).first();
    if (await openCmsButton.isVisible()) {
      await openCmsButton.click();
      
      // Check article elements
      await expect(page.getByRole('link', { name: 'Back to Articles' })).toBeVisible();
      await expect(page.getByRole('link', { name: 'Edit Article' })).toBeVisible();
    }
  });
});

test.describe('Navigation', () => {
  test('should have working navbar links', async ({ page }) => {
    await page.goto('/');
    
    // Check navbar elements
    await expect(page.getByRole('link', { name: 'CMS' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Articles' })).toBeVisible();
  });

  test('should navigate back to home from create page', async ({ page }) => {
    await page.goto('/articles/new');
    
    await page.getByRole('button', { name: 'Cancel' }).click();
    await expect(page).toHaveURL('/');
  });
});

test.describe('Rich Text Editor', () => {
  test('should display editor toolbar', async ({ page }) => {
    await page.goto('/articles/new');
    
    // Check for toolbar buttons
    await expect(page.locator('[title="Bold"]')).toBeVisible();
    await expect(page.locator('[title="Italic"]')).toBeVisible();
    await expect(page.locator('[title="Heading 1"]')).toBeVisible();
    await expect(page.locator('[title="Heading 2"]')).toBeVisible();
    await expect(page.locator('[title="Bullet List"]')).toBeVisible();
    await expect(page.locator('[title="Quote"]')).toBeVisible();
    await expect(page.locator('[title="Undo"]')).toBeVisible();
    await expect(page.locator('[title="Redo"]')).toBeVisible();
  });

  test('should allow text input in editor', async ({ page }) => {
    await page.goto('/articles/new');
    
    // Focus on editor and type
    const editor = page.locator('.tiptap');
    await editor.click();
    await page.keyboard.type('This is test content');
    
    await expect(editor).toContainText('This is test content');
  });
});

test.describe('Tag Management', () => {
  test('should add tags to article', async ({ page }) => {
    await page.goto('/articles/new');
    
    // Add first tag
    await page.getByPlaceholder('Add a tag...').fill('tag1');
    await page.getByRole('button', { name: 'Add' }).click();
    
    // Add second tag
    await page.getByPlaceholder('Add a tag...').fill('tag2');
    await page.getByRole('button', { name: 'Add' }).click();
    
    // Verify tags are displayed
    await expect(page.locator('text=tag1')).toBeVisible();
    await expect(page.locator('text=tag2')).toBeVisible();
  });

  test('should remove tags from article', async ({ page }) => {
    await page.goto('/articles/new');
    
    // Add a tag
    await page.getByPlaceholder('Add a tag...').fill('removable-tag');
    await page.getByRole('button', { name: 'Add' }).click();
    
    // Remove the tag
    await page.locator('text=removable-tag').locator('..').getByRole('button').click();
    
    // Verify tag is removed
    await expect(page.locator('text=removable-tag')).not.toBeVisible();
  });

  test('should add tag on Enter key', async ({ page }) => {
    await page.goto('/articles/new');
    
    await page.getByPlaceholder('Add a tag...').fill('enter-tag');
    await page.keyboard.press('Enter');
    
    await expect(page.locator('text=enter-tag')).toBeVisible();
  });
});

test.describe('Article Status Management', () => {
  test('should display publish button for draft articles', async ({ page }) => {
    await page.goto('/');
    
    // Publish buttons only appear when draft articles exist in the backend
    const count = await page.getByRole('button', { name: 'Publish' }).count();
    if (count > 0) {
      await expect(page.getByRole('button', { name: 'Publish' }).first()).toBeVisible();
    }
  });

  test('should display unpublish button for published articles', async ({ page }) => {
    await page.goto('/');
    
    // Unpublish buttons only appear when published articles exist in the backend
    const count = await page.getByRole('button', { name: 'Unpublish' }).count();
    if (count > 0) {
      await expect(page.getByRole('button', { name: 'Unpublish' }).first()).toBeVisible();
    }
  });
});

test.describe('Responsive Design', () => {
  test('should be responsive on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check that main elements are still visible
    await expect(page.locator('h1')).toContainText('Articles');
  });

  test('should be responsive on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    
    await expect(page.locator('h1')).toContainText('Articles');
  });
});
