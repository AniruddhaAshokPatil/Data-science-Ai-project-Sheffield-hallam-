import { useEffect, useRef, useState } from 'react';

/**
 * Very small WebSocket hook for beginners.
 * - Keeps connection open
 * - Reports status ('idle' | 'connecting' | 'open' | 'closed' | 'error')
 * - Exposes lastMessage
 */
export default function useWebSocket(url) {
  const wsRef = useRef(null);
  const [status, setStatus] = useState('idle');
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    if (!url) return;

    setStatus('connecting');
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setStatus('open');
    ws.onmessage = (ev) => setLastMessage(ev);
    ws.onerror = () => setStatus('error');
    ws.onclose = () => setStatus('closed');

    // Keep-alive ping every 20s (server expects receive_text loop)
    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, 20000);

    return () => {
      clearInterval(ping);
      try { ws.close(); } catch {}
    };
  }, [url]);

  return { status, lastMessage };
}
