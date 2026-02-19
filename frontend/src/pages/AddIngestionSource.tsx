import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_HOST = import.meta.env.VITE_API_URL ? '' : 'http://localhost:8000';

type SourceType = 'rss' | 'youtube' | 'pdf';

const AddIngestionSource: React.FC = () => {
  const navigate = useNavigate();
  const [sourceType, setSourceType] = useState<SourceType>('rss');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // RSS Form State
  const [rssFeedUrl, setRssFeedUrl] = useState('');
  const [rssSourceType, setRssSourceType] = useState('news_primary');
  const [rssMaxEntries, setRssMaxEntries] = useState('10');

  // YouTube Form State
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [youtubeTitle, setYoutubeTitle] = useState('');
  const [youtubeAuthor, setYoutubeAuthor] = useState('');

  // PDF Form State
  const [pdfUrl, setPdfUrl] = useState('');
  const [pdfTitle, setPdfTitle] = useState('');
  const [pdfAuthor, setPdfAuthor] = useState('');
  const [pdfSourceType, setPdfSourceType] = useState('court_filing');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      let endpoint = '';
      let body: any = {};

      switch (sourceType) {
        case 'rss':
          endpoint = '/api/ingestion/rss';
          body = {
            feed_url: rssFeedUrl,
            source_type: rssSourceType,
            max_entries: parseInt(rssMaxEntries),
          };
          break;

        case 'youtube':
          endpoint = '/api/ingestion/youtube';
          body = {
            video_url: youtubeUrl,
            title: youtubeTitle,
            author: youtubeAuthor || null,
          };
          break;

        case 'pdf':
          endpoint = '/api/ingestion/pdf';
          body = {
            pdf_url: pdfUrl,
            title: pdfTitle,
            author: pdfAuthor || null,
            source_type: pdfSourceType,
            save_locally: true,
          };
          break;
      }

      const response = await fetch(`${API_HOST}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to ingest source');
      }

      await response.json();
      alert('Source ingested successfully!');
      navigate('/ingestion');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-6">
        <button
          onClick={() => navigate('/ingestion')}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Queue
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Add Ingestion Source</h1>
        <p className="text-gray-600 mt-1">
          Manually add a source for ingestion and processing
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit}>
          {/* Source Type Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source Type
            </label>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setSourceType('rss')}
                className={`px-4 py-2 rounded-lg border ${
                  sourceType === 'rss'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                RSS Feed
              </button>
              <button
                type="button"
                onClick={() => setSourceType('youtube')}
                className={`px-4 py-2 rounded-lg border ${
                  sourceType === 'youtube'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                YouTube Video
              </button>
              <button
                type="button"
                onClick={() => setSourceType('pdf')}
                className={`px-4 py-2 rounded-lg border ${
                  sourceType === 'pdf'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                PDF Document
              </button>
            </div>
          </div>

          {/* RSS Form */}
          {sourceType === 'rss' && (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Feed URL *
                </label>
                <input
                  type="url"
                  value={rssFeedUrl}
                  onChange={(e) => setRssFeedUrl(e.target.value)}
                  required
                  placeholder="https://example.com/feed.xml"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Source Type
                </label>
                <select
                  value={rssSourceType}
                  onChange={(e) => setRssSourceType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="news_primary">News (Primary)</option>
                  <option value="news_secondary">News (Secondary)</option>
                  <option value="ngo_report">NGO Report</option>
                  <option value="government_report">Government Report</option>
                  <option value="academic">Academic</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Entries
                </label>
                <input
                  type="number"
                  value={rssMaxEntries}
                  onChange={(e) => setRssMaxEntries(e.target.value)}
                  min="1"
                  max="100"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </>
          )}

          {/* YouTube Form */}
          {sourceType === 'youtube' && (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Video URL *
                </label>
                <input
                  type="url"
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  required
                  placeholder="https://youtube.com/watch?v=..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={youtubeTitle}
                  onChange={(e) => setYoutubeTitle(e.target.value)}
                  required
                  placeholder="Video title"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Author
                </label>
                <input
                  type="text"
                  value={youtubeAuthor}
                  onChange={(e) => setYoutubeAuthor(e.target.value)}
                  placeholder="Channel name or creator"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </>
          )}

          {/* PDF Form */}
          {sourceType === 'pdf' && (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  PDF URL *
                </label>
                <input
                  type="url"
                  value={pdfUrl}
                  onChange={(e) => setPdfUrl(e.target.value)}
                  required
                  placeholder="https://example.com/document.pdf"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={pdfTitle}
                  onChange={(e) => setPdfTitle(e.target.value)}
                  required
                  placeholder="Document title"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Author
                </label>
                <input
                  type="text"
                  value={pdfAuthor}
                  onChange={(e) => setPdfAuthor(e.target.value)}
                  placeholder="Document author"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Source Type
                </label>
                <select
                  value={pdfSourceType}
                  onChange={(e) => setPdfSourceType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="court_filing">Court Filing</option>
                  <option value="government_report">Government Report</option>
                  <option value="foia">FOIA</option>
                  <option value="academic">Academic</option>
                  <option value="ngo_report">NGO Report</option>
                  <option value="leaked_document">Leaked Document</option>
                </select>
              </div>
            </>
          )}

          {/* Submit Button */}
          <div className="flex gap-3 mt-6">
            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? 'Processing...' : 'Ingest Source'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/ingestion')}
              disabled={submitting}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddIngestionSource;
