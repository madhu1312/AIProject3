export interface Article {
  id: string;
  title: string;
  content: string;
  excerpt: string;
  status: 'draft' | 'published' | 'archived';
  author: string;
  slug: string;
  created: string;
  updated: string;
  published?: string;
  tags: string[];
}

export interface ArticleFormData {
  title: string;
  content: string;
  excerpt: string;
  status: 'draft' | 'published' | 'archived';
  tags: string[];
}

export type ArticleStatus = 'draft' | 'published' | 'archived';
