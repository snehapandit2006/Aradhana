import { useState, useEffect, useCallback } from 'react';
import { BirthData, Message } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useSession = () => {
  const [sessionId, setSessionId] = useState<string>('');
  const [birthData, setBirthData] = useState<BirthData | null>(null);
  const [history, setHistory] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize or fetch session ID
  useEffect(() => {
    let id = localStorage.getItem('astro_session_id');
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem('astro_session_id', id);
    }
    setSessionId(id);
  }, []);

  // Fetch session history once session ID is resolved
  const fetchHistory = useCallback(async (id: string) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/history/${id}`);
      if (!response.ok) {
        throw new Error('Failed to load your reading history from the stars.');
      }
      const data = await response.json();
      
      if (data.birth_data) {
        setBirthData(data.birth_data);
      }
      if (data.history) {
        // Map database response to Message format
        const mappedHistory = data.history.map((msg: any, index: number) => ({
          id: `hist_${index}`,
          role: msg.role,
          content: msg.content
        }));
        setHistory(mappedHistory);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Unable to connect to the celestial backend.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (sessionId) {
      fetchHistory(sessionId);
    }
  }, [sessionId, fetchHistory]);

  const updateBirthData = (data: BirthData) => {
    setBirthData(data);
  };

  const addMessageToHistory = (msg: Message) => {
    setHistory((prev) => [...prev, msg]);
  };

  const resetSession = async () => {
    if (!sessionId) return;
    setLoading(true);
    try {
      // Notify backend to clear session
      await fetch(`${API_URL}/session/${sessionId}`, { method: 'DELETE' });
    } catch (err) {
      console.error('Failed to notify backend of session deletion:', err);
    }

    // Reset local state
    localStorage.removeItem('astro_session_id');
    setBirthData(null);
    setHistory([]);
    setError(null);
    
    // Generate new session ID
    const newId = crypto.randomUUID();
    localStorage.setItem('astro_session_id', newId);
    setSessionId(newId);
    setLoading(false);
  };

  return {
    sessionId,
    birthData,
    history,
    loading,
    error,
    updateBirthData,
    addMessageToHistory,
    resetSession,
    setHistory
  };
};
