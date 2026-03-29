import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles.css';

// I mount the React app here because this file is the frontend entry point
// that connects my App component to the root element in index.html.
createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* I keep StrictMode during development because it helps me notice unsafe
        React patterns earlier while I build the dashboard. */}
    <App />
  </React.StrictMode>
);
