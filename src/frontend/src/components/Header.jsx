export default function Header({ wsConnected, apiStatus }) {
  return (
    <header className="header">
      <div>
        {/* I keep the title in the header so users always know which project view
            they are on, even when the dashboard grows larger later. */}
        <h1>Fraud Detection Command Dashboard</h1>
        <p className="header-copy">
          I use this dashboard to watch live risk flow, test scoring routes, and confirm model readiness before release decisions.
        </p>
      </div>
      <div className="header-statuses">
        <div className="status">
          {/* I use a conditional class here because the small status dot is an
              easy visual cue for live WebSocket connectivity. */}
          <span className={`dot ${wsConnected ? 'up' : 'down'}`} />
          WebSocket: {wsConnected ? 'Connected' : 'Disconnected'}
        </div>
        <div className="status">
          <span className={`dot ${apiStatus === 'ready' ? 'up' : apiStatus === 'degraded' ? 'warn' : 'down'}`} />
          API: {apiStatus || 'unknown'}
        </div>
      </div>
    </header>
  );
}
