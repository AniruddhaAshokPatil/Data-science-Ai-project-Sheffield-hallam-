export default function Header({ wsConnected }) {
  return (
    <header className="header">
      <h1>Fraud Detection Dashboard (MVP)</h1>
      <div className="status">
        <span className={`dot ${wsConnected ? 'up' : 'down'}`} />
        WebSocket: {wsConnected ? 'Connected' : 'Disconnected'}
      </div>
    </header>
  );
}
