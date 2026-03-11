import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { articleService } from '../services';
import type { Article } from '../types';
import { format } from 'date-fns';
import { Edit, ArrowLeft, Calendar, User, Tag } from 'lucide-react';

export const ArticleView = () => {
  const { id } = useParams<{ id: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);

  const loadArticle = async () => {
    if (!id) return;
    setLoading(true);
    const data = await articleService.getById(id);
    setArticle(data);
    setLoading(false);
  };

  useEffect(() => {
    loadArticle();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'N/A';
    return format(new Date(dateString), 'MMMM dd, yyyy');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-bold text-white mb-4">Article Not Found</h2>
        <Link to="/" className="text-indigo-400 hover:text-indigo-300">
          Return to Articles
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <Link
          to="/"
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft size={20} />
          Back to Articles
        </Link>
        <Link
          to={`/articles/${article.id}/edit`}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors"
        >
          <Edit size={18} />
          Edit Article
        </Link>
      </div>

      {/* Article Content */}
      <article className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="p-8">
          {/* Status Badge */}
          <div className="mb-4">
            <span
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                article.status === 'published'
                  ? 'bg-green-500/20 text-green-400'
                  : article.status === 'draft'
                  ? 'bg-yellow-500/20 text-yellow-400'
                  : 'bg-gray-500/20 text-gray-400'
              }`}
            >
              {article.status.charAt(0).toUpperCase() + article.status.slice(1)}
            </span>
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-white mb-4">{article.title}</h1>

          {/* Meta */}
          <div className="flex flex-wrap items-center gap-6 text-gray-400 text-sm mb-6 pb-6 border-b border-gray-700">
            <div className="flex items-center gap-2">
              <User size={16} />
              <span>{article.author}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar size={16} />
              <span>Created: {formatDate(article.created)}</span>
            </div>
            {article.published && (
              <div className="flex items-center gap-2">
                <Calendar size={16} />
                <span>Published: {formatDate(article.published)}</span>
              </div>
            )}
          </div>

          {/* Excerpt */}
          {article.excerpt && (
            <p className="text-xl text-gray-300 mb-6 italic">{article.excerpt}</p>
          )}

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="flex items-center gap-2 mb-6">
              <Tag size={16} className="text-gray-400" />
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Content */}
          <div
            className="prose prose-invert max-w-none"
            dangerouslySetInnerHTML={{ __html: article.content }}
          />
        </div>
      </article>
    </div>
  );
};

export default ArticleView;
