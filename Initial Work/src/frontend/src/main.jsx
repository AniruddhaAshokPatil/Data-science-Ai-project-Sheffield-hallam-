import React, { Component, StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles.css';


class FrontendErrorBoundary extends Component {
  // I use an error boundary here so a frontend crash shows a visible message
  // on screen instead of leaving the whole dashboard blank.
  constructor(props) {
    super(props);
    this.state = { hasError: false, message: '' };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      message: error instanceof Error ? error.message : 'Unknown frontend error.'
    };
  }

  componentDidCatch(error) {
    // I also log the error here so I can inspect it in the browser console
    // while still showing a readable message inside the page.
    console.error('I caught a frontend rendering error:', error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '32px', color: '#edf5ff', fontFamily: '"IBM Plex Sans", "Segoe UI", sans-serif' }}>
          <h1>Frontend Error</h1>
          <p>I could not finish rendering the dashboard.</p>
          <pre style={{ whiteSpace: 'pre-wrap', color: '#fecaca' }}>{this.state.message}</pre>
        </div>
      );
    }

    return this.props.children;
  }
}

// I mount the React app here because this file is the frontend entry point
// that connects my App component to the root element in index.html.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/* I keep StrictMode during development because it helps me notice unsafe
        React patterns earlier while I build the dashboard. */}
    <FrontendErrorBoundary>
      <App />
    </FrontendErrorBoundary>
  </StrictMode>
);
