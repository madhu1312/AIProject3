import type { Article } from '../types';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';
import { Edit, Eye, ExternalLink, Trash2, Globe, FileEdit } from 'lucide-react';

interface ArticleCardProps {
  article: Article;
  onDelete: (id: string) => void;
  onPublish: (id: string) => void;
  onUnpublish: (id: string) => void;
}

export const ArticleCard = ({ article, onDelete, onPublish, onUnpublish }: ArticleCardProps) => {
  const statusColors = {
    draft: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    published: 'bg-green-500/20 text-green-400 border-green-500/30',
    archived: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'N/A';
    return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-white mb-2">{article.title}</h3>
          <p className="text-gray-400 text-sm line-clamp-2">{article.excerpt || 'No excerpt available'}</p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium border ${statusColors[article.status]}`}
        >
          {article.status.charAt(0).toUpperCase() + article.status.slice(1)}
        </span>
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
        <div>
          <span className="text-gray-500 block">Created</span>
          <span className="text-gray-300">{formatDate(article.created)}</span>
        </div>
        <div>
          <span className="text-gray-500 block">Last Edited</span>
          <span className="text-gray-300">{formatDate(article.updated)}</span>
        </div>
        <div>
          <span className="text-gray-500 block">Published</span>
          <span className="text-gray-300">{formatDate(article.published)}</span>
        </div>
      </div>

      {/* Tags */}
      {article.tags && article.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {article.tags.map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 pt-4 border-t border-gray-700">
        <Link
          to={`/articles/${article.id}/edit`}
          className="flex items-center gap-1 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm transition-colors"
        >
          <Edit size={14} />
          Edit
        </Link>
        <Link
          to={`/articles/${article.id}`}
          className="flex items-center gap-1 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm transition-colors"
        >
          <FileEdit size={14} />
          Open in CMS
        </Link>
        {article.status === 'published' && (
          <Link
            to={`/preview/${article.slug}`}
            target="_blank"
            className="flex items-center gap-1 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm transition-colors"
          >
            <ExternalLink size={14} />
            View in Browser
          </Link>
        )}
        <div className="flex-1" />
        {article.status === 'draft' ? (
          <button
            onClick={() => onPublish(article.id)}
            className="flex items-center gap-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded text-sm transition-colors"
          >
            <Globe size={14} />
            Publish
          </button>
        ) : article.status === 'published' ? (
          <button
            onClick={() => onUnpublish(article.id)}
            className="flex items-center gap-1 px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 text-white rounded text-sm transition-colors"
          >
            <Eye size={14} />
            Unpublish
          </button>
        ) : null}
        <button
          onClick={() => onDelete(article.id)}
          className="flex items-center gap-1 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
        >
          <Trash2 size={14} />
          Delete
        </button>
      </div>
    </div>
  );
};

export default ArticleCard;
