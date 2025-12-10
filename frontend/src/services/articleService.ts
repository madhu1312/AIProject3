import pb from '../lib/pocketbase';
import type { Article, ArticleFormData } from '../types';

const COLLECTION_NAME = 'articles';

// Helper to generate slug from title
const generateSlug = (title: string): string => {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
};

export const articleService = {
  // Get all articles
  async getAll(): Promise<Article[]> {
    try {
      const records = await pb.collection(COLLECTION_NAME).getFullList({
        sort: '-created',
      });
      return records as unknown as Article[];
    } catch (error) {
      console.error('Error fetching articles:', error);
      return [];
    }
  },

  // Get single article by ID
  async getById(id: string): Promise<Article | null> {
    try {
      const record = await pb.collection(COLLECTION_NAME).getOne(id);
      return record as unknown as Article;
    } catch (error) {
      console.error('Error fetching article:', error);
      return null;
    }
  },

  // Get article by slug
  async getBySlug(slug: string): Promise<Article | null> {
    try {
      const record = await pb.collection(COLLECTION_NAME).getFirstListItem(`slug="${slug}"`);
      return record as unknown as Article;
    } catch (error) {
      console.error('Error fetching article by slug:', error);
      return null;
    }
  },

  // Create new article
  async create(data: ArticleFormData): Promise<Article | null> {
    try {
      const slug = generateSlug(data.title);
      const record = await pb.collection(COLLECTION_NAME).create({
        ...data,
        slug,
        author: 'Admin', // Default author
        tags: data.tags || [],
      });
      return record as unknown as Article;
    } catch (error) {
      console.error('Error creating article:', error);
      return null;
    }
  },

  // Update article
  async update(id: string, data: Partial<ArticleFormData>): Promise<Article | null> {
    try {
      const updateData: Record<string, unknown> = { ...data };
      
      // Update slug if title changed
      if (data.title) {
        updateData.slug = generateSlug(data.title);
      }
      
      // Set published date if status changed to published
      if (data.status === 'published') {
        const existing = await pb.collection(COLLECTION_NAME).getOne(id);
        if (existing && (existing as unknown as Article).status !== 'published') {
          updateData.published = new Date().toISOString();
        }
      }
      
      const record = await pb.collection(COLLECTION_NAME).update(id, updateData);
      return record as unknown as Article;
    } catch (error) {
      console.error('Error updating article:', error);
      return null;
    }
  },

  // Delete article
  async delete(id: string): Promise<boolean> {
    try {
      await pb.collection(COLLECTION_NAME).delete(id);
      return true;
    } catch (error) {
      console.error('Error deleting article:', error);
      return false;
    }
  },

  // Publish article
  async publish(id: string): Promise<Article | null> {
    return this.update(id, { status: 'published' });
  },

  // Unpublish article
  async unpublish(id: string): Promise<Article | null> {
    return this.update(id, { status: 'draft' });
  },

  // Archive article
  async archive(id: string): Promise<Article | null> {
    return this.update(id, { status: 'archived' });
  },
};

export default articleService;
