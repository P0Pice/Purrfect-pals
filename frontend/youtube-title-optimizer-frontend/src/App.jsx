import { useState } from 'react';
import './App.css';

function App() {
  const [title, setTitle] = useState('');
  const [suggestions, setSuggestions] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleOptimizeTitle = async () => {
    setIsLoading(true);
    setError(null);
    setSuggestions(''); // Clear previous suggestions

    try {
      const response = await fetch('http://localhost:5000/api/optimize-title', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSuggestions(data.suggestions);
    } catch (e) {
      setError(e.message || 'Failed to fetch suggestions. Make sure the backend server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>YouTube Title Optimizer</h1>
      </header>
      <main>
        <div className="input-section">
          <label htmlFor="videoTitle">Enter your YouTube Video Title:</label>
          <input
            type="text"
            id="videoTitle"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., My Awesome Cat Video"
            disabled={isLoading}
          />
          <button onClick={handleOptimizeTitle} disabled={isLoading}>
            {isLoading ? 'Optimizing...' : 'Optimize Title'}
          </button>
        </div>
        <div className="suggestions-section">
          <h2>Suggestions:</h2>
          {isLoading && <p>Loading suggestions...</p>}
          {error && <p className="error-message">Error: {error}</p>}
          {suggestions && !isLoading && !error && (
            <pre>{suggestions}</pre>
          )}
          {!suggestions && !isLoading && !error && (
            <p>Enter a title above and click "Optimize Title" to see suggestions.</p>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
