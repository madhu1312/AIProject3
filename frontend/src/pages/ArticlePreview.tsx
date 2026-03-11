import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { articleService } from '../services';
import type { Article } from '../types';
import { format } from 'date-fns';
import { ArrowLeft, Calendar, User, Tag } from 'lucide-react';

export const ArticlePreview = () => {
  const { slug } = useParams<{ slug: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);

  const loadArticle = async () => {
    if (!slug) return;
    setLoading(true);
    const data = await articleService.getBySlug(slug);
    setArticle(data);
    setLoading(false);
  };

  useEffect(() => {
    loadArticle();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'N/A';
    return format(new Date(dateString), 'MMMM dd, yyyy');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!article || article.status !== 'published') {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Article Not Found</h2>
          <p className="text-gray-600 mb-6">This article may not be published or doesn't exist.</p>
          <Link
            to="/"
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            Return to CMS
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4">
        <div className="max-w-4xl mx-auto px-4">
          <Link
            to="/"
            className="flex items-center gap-2 text-white/80 hover:text-white transition-colors text-sm"
          >
            <ArrowLeft size={16} />
            Back to CMS
          </Link>
        </div>
      </div>

      {/* Article */}
      <article className="max-w-4xl mx-auto px-4 py-12">
        {/* Title */}
        <h1 className="text-5xl font-bold text-gray-900 mb-6 leading-tight">
          {article.title}
        </h1>

        {/* Meta */}
        <div className="flex flex-wrap items-center gap-6 text-gray-500 text-sm mb-8 pb-8 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <User size={16} />
            <span className="font-medium">{article.author}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar size={16} />
            <span>{formatDate(article.published || article.created)}</span>
          </div>
        </div>

        {/* Excerpt */}
        {article.excerpt && (
          <p className="text-2xl text-gray-600 mb-8 leading-relaxed">
            {article.excerpt}
          </p>
        )}

        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex items-center gap-2 mb-8">
            <Tag size={16} className="text-gray-400" />
            <div className="flex flex-wrap gap-2">
              {article.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Content */}
        <div
          className="prose prose-lg max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-a:text-indigo-600"
          dangerouslySetInnerHTML={{ __html: article.content }}
        />
      </article>

      {/* Footer */}
      <footer className="bg-gray-100 py-8 mt-16">
        <div className="max-w-4xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>Published with CMS React App</p>
        </div>
      </footer>
    </div>
  );
};

export default ArticlePreview;
