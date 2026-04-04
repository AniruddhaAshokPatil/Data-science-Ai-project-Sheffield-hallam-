import { useEffect, useRef, useState } from 'react';

/**
 * Very small WebSocket hook for beginners.
 * - Keeps connection open
 * - Reports status ('idle' | 'connecting' | 'open' | 'closed' | 'error')
 * - Exposes lastMessage
 */
export default function useWebSocket(url) {
  // I store the WebSocket instance in a ref because I want the connection to
  // persist across renders without causing extra re-renders itself.
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const [status, setStatus] = useState('idle');
  const [lastMessage, setLastMessage] = useState(null);
  const [lastError, setLastError] = useState('');

  useEffect(() => {
    // I return early when there is no URL because the hook should do nothing
    // until the frontend knows which WebSocket endpoint to connect to.
    if (!url) return undefined;

    let cancelled = false;
    let ping = null;

    function connect(attempt = 0) {
      if (cancelled) return;

      setStatus('connecting');
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('open');
        setLastError('');
      };

      ws.onmessage = (ev) => {
        try {
          setLastMessage(JSON.parse(ev.data));
        } catch {
          setLastMessage(ev.data);
        }
      };

      ws.onerror = () => {
        setStatus('error');
        setLastError('I could not keep the live WebSocket connection open.');
      };

      ws.onclose = () => {
        setStatus('closed');
        if (!cancelled) {
          const delayMs = Math.min(1000 * 2 ** attempt, 10000);
          reconnectTimeoutRef.current = window.setTimeout(() => connect(attempt + 1), delayMs);
        }
      };

      ping = window.setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 20000);
    }

    connect();

    return () => {
      // I clean up the interval and close the socket so unmounted components
      // do not leave background connections running.
      cancelled = true;
      if (ping) {
        window.clearInterval(ping);
      }
      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
      }
      try {
        wsRef.current?.close();
      } catch {
        setStatus('closed');
      }
    };
  }, [url]);

  return { status, lastMessage, lastError };
}
