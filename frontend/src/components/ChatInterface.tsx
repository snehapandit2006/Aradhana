import React, { useState, useRef, useEffect } from 'react';
import { Message, ToolActivity, BirthData } from '../types';
import { MessageBubble } from './MessageBubble';
import { ToolActivityFeed } from './ToolActivityFeed';
import { ConstellationLoader } from './ConstellationLoader';
import { Send, LogOut, Compass, Sparkles } from 'lucide-react';

interface ChatInterfaceProps {
  messages: Message[];
  birthData: BirthData | null;
  streaming: boolean;
  toolActivities: ToolActivity[];
  currentStreamedContent: string;
  onSendMessage: (message: string) => void;
  onResetSession: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  birthData,
  streaming,
  toolActivities,
  currentStreamedContent,
  onSendMessage,
  onResetSession,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Scroll to bottom on message updates or active token stream changes
  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamedContent, streaming, toolActivities]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || streaming) return;
    onSendMessage(input.trim());
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-[#0a0e1a]/80 backdrop-blur-md rounded-3xl border border-cosmic-lavender/25 overflow-hidden shadow-nebula">
      {/* Session Top Bar Banner */}
      <div className="flex items-center justify-between px-6 py-4 bg-cosmic-slate/90 border-b border-cosmic-lavender/10">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-cosmic-gold/10 border border-cosmic-gold/30 text-cosmic-gold">
            <Compass className="w-5 h-5 animate-spin" style={{ animationDuration: '40s' }} />
          </div>
          <div>
            <h1 className="text-base font-serif text-slate-100 font-medium flex items-center">
              {birthData?.name || 'Astro Seeker'}
              <Sparkles className="w-3.5 h-3.5 ml-1.5 text-cosmic-gold animate-pulse" />
            </h1>
            <p className="text-[10px] text-cosmic-lavender tracking-wide uppercase mt-0.5">
              Chart Aligned: {birthData?.place}
            </p>
          </div>
        </div>

        <button
          onClick={onResetSession}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-rose-500/20 text-rose-400 text-xs font-serif bg-rose-500/5 hover:bg-rose-500/10 active:scale-95 transition"
          title="Clear session and birth details"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Reset Session</span>
        </button>
      </div>

      {/* Messages Scroll Panel */}
      <div 
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto p-6 space-y-4"
      >
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 max-w-md mx-auto space-y-4">
            <div className="w-16 h-16 rounded-full bg-cosmic-gold/5 border border-cosmic-gold/20 flex items-center justify-center text-cosmic-gold mb-2 shadow-gold-glow">
              <Sparkles className="w-8 h-8 animate-pulse" />
            </div>
            <h3 className="text-xl font-serif text-cosmic-gold">Spiritual Alignment Complete</h3>
            <p className="text-xs text-cosmic-lavender leading-relaxed">
              Welcome, <span className="text-slate-100 font-semibold">{birthData?.name}</span>. Your birth coordinates are recorded. Ask about your planetary alignments, daily transits, career outlook, or love aspects.
            </p>
            <div className="grid grid-cols-2 gap-2 w-full pt-4 text-left">
              <button 
                onClick={() => onSendMessage("Calculate my birth chart details")}
                className="p-2.5 bg-cosmic-slate/50 border border-cosmic-lavender/10 rounded-xl text-[11px] text-slate-300 hover:border-cosmic-gold hover:text-cosmic-gold transition text-left"
              >
                🪐 Compute Natal Chart
              </button>
              <button 
                onClick={() => onSendMessage("What are my current transits today?")}
                className="p-2.5 bg-cosmic-slate/50 border border-cosmic-lavender/10 rounded-xl text-[11px] text-slate-300 hover:border-cosmic-gold hover:text-cosmic-gold transition text-left"
              >
                🔭 Daily Transits
              </button>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {/* Dynamic active stream message bubble */}
        {streaming && currentStreamedContent && (
          <MessageBubble
            message={{
              id: 'active_stream',
              role: 'assistant',
              content: currentStreamedContent,
            }}
          />
        )}

        {/* Tool activity logs */}
        {streaming && <ToolActivityFeed activities={toolActivities} />}

        {/* loader */}
        {streaming && !currentStreamedContent && <ConstellationLoader />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Panel */}
      <form 
        onSubmit={handleSubmit}
        className="p-4 bg-cosmic-slate/60 border-t border-cosmic-lavender/10 flex items-center space-x-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={streaming}
          placeholder={streaming ? "AstroAgent is reading the charts..." : "Ask the stars anything..."}
          className="flex-1 px-5 py-3.5 bg-cosmic-dark/95 border border-cosmic-lavender/25 rounded-2xl text-slate-200 text-sm placeholder-slate-500 focus:outline-none focus:border-cosmic-gold focus:shadow-gold-glow transition"
        />
        <button
          type="submit"
          disabled={!input.trim() || streaming}
          className="p-3.5 rounded-2xl bg-gradient-to-r from-cosmic-gold to-yellow-600 border border-cosmic-gold/30 text-cosmic-dark hover:shadow-gold-glow disabled:opacity-40 disabled:pointer-events-none active:scale-95 transition"
        >
          <Send className="w-4.5 h-4.5" />
        </button>
      </form>
    </div>
  );
};
