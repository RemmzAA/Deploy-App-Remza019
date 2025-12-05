import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const API = process.env.REACT_APP_BACKEND_URL;

// Semantic Search Component
const SemanticSearch = () => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);

  useEffect(() => {
    // Load search history from localStorage
    const history = localStorage.getItem('019solutions_search_history');
    if (history) {
      setSearchHistory(JSON.parse(history));
    }
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const response = await axios.post(`${API}/api/search/semantic`, {
        query: searchQuery,
        limit: 10
      });

      setSearchResults(response.data.results || []);
      
      // Add to search history
      const newHistory = [searchQuery, ...searchHistory.slice(0, 9)];
      setSearchHistory(newHistory);
      localStorage.setItem('019solutions_search_history', JSON.stringify(newHistory));

    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    }
    setIsSearching(false);
  };

  const clearSearchHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('019solutions_search_history');
  };

  return (
    <section id="search" className="semantic-search-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">AI-Powered Semantic Search</h2>
          <p className="section-subtitle">Find exactly what you're looking for with intelligent search</p>
        </div>

        <div className="search-container glass">
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-group">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for services, projects, or information..."
                className="search-input"
                disabled={isSearching}
              />
              <button 
                type="submit" 
                className="search-btn"
                disabled={isSearching}
              >
                {isSearching ? (
                  <div className="loading-spinner">🔍</div>
                ) : (
                  '🔍'
                )}
              </button>
            </div>
          </form>

          {searchHistory.length > 0 && (
            <div className="search-history">
              <div className="history-header">
                <h4>Recent Searches</h4>
                <button onClick={clearSearchHistory} className="clear-history">
                  Clear
                </button>
              </div>
              <div className="history-tags">
                {searchHistory.map((query, index) => (
                  <button
                    key={index}
                    className="history-tag"
                    onClick={() => setSearchQuery(query)}
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {searchResults.length > 0 && (
          <div className="search-results">
            <h3>Search Results ({searchResults.length})</h3>
            <div className="results-grid">
              {searchResults.map((result, index) => (
                <SearchResultCard key={index} result={result} />
              ))}
            </div>
          </div>
        )}

        {searchQuery && !isSearching && searchResults.length === 0 && (
          <div className="no-results">
            <div className="no-results-content glass">
              <h3>No results found</h3>
              <p>Try different keywords or check out our services and portfolio</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

// Search Result Card Component
const SearchResultCard = ({ result }) => {
  const getResultIcon = (type) => {
    switch (type) {
      case 'service': return '⚙️';
      case 'project': return '🚀';
      case 'freelancer': return '👤';
      case 'blog': return '📝';
      default: return '📄';
    }
  };

  const getResultTypeLabel = (type) => {
    switch (type) {
      case 'service': return 'Service';
      case 'project': return 'Portfolio Project';
      case 'freelancer': return 'Freelancer';
      case 'blog': return 'Blog Post';
      default: return 'Content';
    }
  };

  return (
    <div className="result-card glass luxury-hover">
      <div className="result-header">
        <div className="result-icon">
          {getResultIcon(result.type)}
        </div>
        <div className="result-meta">
          <span className="result-type">{getResultTypeLabel(result.type)}</span>
          <span className="result-score">
            {Math.round(result.score * 100)}% match
          </span>
        </div>
      </div>
      
      <div className="result-content">
        <h4 className="result-title">{result.title}</h4>
        <p className="result-description">
          {result.description.substring(0, 120)}...
        </p>
        
        {result.tags && result.tags.length > 0 && (
          <div className="result-tags">
            {result.tags.slice(0, 3).map((tag, index) => (
              <span key={index} className="result-tag">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="result-actions">
        <button className="view-result-btn">
          View Details
        </button>
      </div>
    </div>
  );
};

export default SemanticSearch;