import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { articleService } from '../services';
import { RichTextEditor } from '../components';
import type { Article, ArticleFormData } from '../types';
import { Save, X, Send, Archive, Trash2 } from 'lucide-react';

export const ArticleEdit = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [article, setArticle] = useState<Article | null>(null);
  const [formData, setFormData] = useState<ArticleFormData>({
    title: '',
    content: '',
    excerpt: '',
    status: 'draft',
    tags: [],
  });
  const [tagInput, setTagInput] = useState('');

  useEffect(() => {
    loadArticle();
  }, [id]);

  const loadArticle = async () => {
    if (!id) return;
    setLoading(true);
    const data = await articleService.getById(id);
    if (data) {
      setArticle(data);
      setFormData({
        title: data.title,
        content: data.content,
        excerpt: data.excerpt,
        status: data.status,
        tags: data.tags || [],
      });
    }
    setLoading(false);
  };

  const handleSave = async () => {
    if (!id || !formData.title.trim()) {
      alert('Please enter a title');
      return;
    }

    setSaving(true);
    const updated = await articleService.update(id, formData);
    if (updated) {
      setArticle(updated);
      alert('Article saved successfully');
    } else {
      alert('Failed to save article');
    }
    setSaving(false);
  };

  const handlePublish = async () => {
    if (!id) return;
    setSaving(true);
    const updated = await articleService.publish(id);
    if (updated) {
      setArticle(updated);
      setFormData({ ...formData, status: 'published' });
    }
    setSaving(false);
  };

  const handleUnpublish = async () => {
    if (!id) return;
    setSaving(true);
    const updated = await articleService.unpublish(id);
    if (updated) {
      setArticle(updated);
      setFormData({ ...formData, status: 'draft' });
    }
    setSaving(false);
  };

  const handleArchive = async () => {
    if (!id) return;
    if (window.confirm('Are you sure you want to archive this article?')) {
      setSaving(true);
      const updated = await articleService.archive(id);
      if (updated) {
        navigate('/');
      }
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (window.confirm('Are you sure you want to delete this article? This action cannot be undone.')) {
      const success = await articleService.delete(id);
      if (success) {
        navigate('/');
      }
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()],
      });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter((t) => t !== tag),
    });
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
        <button
          onClick={() => navigate('/')}
          className="text-indigo-400 hover:text-indigo-300"
        >
          Return to Articles
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Edit Article</h1>
          <p className="text-gray-400 mt-1">
            Status: <span className={`font-medium ${
              formData.status === 'published' ? 'text-green-400' : 
              formData.status === 'draft' ? 'text-yellow-400' : 'text-gray-400'
            }`}>
              {formData.status.charAt(0).toUpperCase() + formData.status.slice(1)}
            </span>
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            <X size={18} />
            Close
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <Save size={18} />
            Save
          </button>
          {formData.status === 'draft' ? (
            <button
              onClick={handlePublish}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <Send size={18} />
              Publish
            </button>
          ) : formData.status === 'published' ? (
            <button
              onClick={handleUnpublish}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              Unpublish
            </button>
          ) : null}
        </div>
      </div>

      <div className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Title
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Enter article title..."
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500 text-lg"
          />
        </div>

        {/* Excerpt */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Excerpt
          </label>
          <textarea
            value={formData.excerpt}
            onChange={(e) => setFormData({ ...formData, excerpt: e.target.value })}
            placeholder="Brief description of the article..."
            rows={2}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500 resize-none"
          />
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Tags
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
              placeholder="Add a tag..."
              className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="button"
              onClick={handleAddTag}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.tags.map((tag) => (
              <span
                key={tag}
                className="flex items-center gap-1 px-3 py-1 bg-indigo-600/30 text-indigo-300 rounded-full text-sm"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-white"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Content Editor */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Content
          </label>
          <RichTextEditor
            content={formData.content}
            onChange={(content) => setFormData({ ...formData, content })}
            placeholder="Start writing your article..."
          />
        </div>

        {/* Danger Zone */}
        <div className="pt-6 border-t border-gray-700">
          <h3 className="text-lg font-medium text-red-400 mb-4">Danger Zone</h3>
          <div className="flex gap-3">
            <button
              onClick={handleArchive}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors disabled:opacity-50"
            >
              <Archive size={18} />
              Archive Article
            </button>
            <button
              onClick={handleDelete}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <Trash2 size={18} />
              Delete Article
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleEdit;
