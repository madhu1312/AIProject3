import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { Article } from '../types';
import { articleService } from '../services';
import { ArticleCard } from '../components';
import { PlusCircle, FileText, Search } from 'lucide-react';

export const ArticleList = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const loadArticles = async () => {
    setLoading(true);
    const data = await articleService.getAll();
    setArticles(data);
    setLoading(false);
  };

  useEffect(() => {
    loadArticles();
  }, []);

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this article?')) {
      const success = await articleService.delete(id);
      if (success) {
        setArticles(articles.filter((a) => a.id !== id));
      }
    }
  };

  const handlePublish = async (id: string) => {
    const updated = await articleService.publish(id);
    if (updated) {
      setArticles(articles.map((a) => (a.id === id ? updated : a)));
    }
  };

  const handleUnpublish = async (id: string) => {
    const updated = await articleService.unpublish(id);
    if (updated) {
      setArticles(articles.map((a) => (a.id === id ? updated : a)));
    }
  };

  const filteredArticles = articles.filter((article) => {
    const matchesSearch =
      article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.excerpt?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || article.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Articles</h1>
          <p className="text-gray-400">Manage your content and publications</p>
        </div>
        <Link
          to="/articles/new"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg text-sm font-medium transition-colors"
        >
          <PlusCircle size={20} />
          Create Document
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search articles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
        >
          <option value="all">All Status</option>
          <option value="draft">Draft</option>
          <option value="published">Published</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {/* Article List */}
      {filteredArticles.length === 0 ? (
        <div className="text-center py-16 bg-gray-800 rounded-lg border border-gray-700">
          <FileText className="mx-auto text-gray-600 mb-4" size={48} />
          <h3 className="text-xl font-medium text-gray-300 mb-2">No articles found</h3>
          <p className="text-gray-500 mb-6">
            {articles.length === 0
              ? "Get started by creating your first article"
              : "No articles match your search criteria"}
          </p>
          {articles.length === 0 && (
            <Link
              to="/articles/new"
              className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <PlusCircle size={20} />
              Create Your First Article
            </Link>
          )}
        </div>
      ) : (
        <div className="grid gap-6">
          {filteredArticles.map((article) => (
            <ArticleCard
              key={article.id}
              article={article}
              onDelete={handleDelete}
              onPublish={handlePublish}
              onUnpublish={handleUnpublish}
            />
          ))}
        </div>
      )}

      {/* Stats */}
      <div className="mt-8 grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-white">{articles.length}</div>
          <div className="text-gray-400 text-sm">Total Articles</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-green-400">
            {articles.filter((a) => a.status === 'published').length}
          </div>
          <div className="text-gray-400 text-sm">Published</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-yellow-400">
            {articles.filter((a) => a.status === 'draft').length}
          </div>
          <div className="text-gray-400 text-sm">Drafts</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-gray-400">
            {articles.filter((a) => a.status === 'archived').length}
          </div>
          <div className="text-gray-400 text-sm">Archived</div>
        </div>
      </div>
    </div>
  );
};

export default ArticleList;
