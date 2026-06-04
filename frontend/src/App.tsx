import React from 'react';
import { useSession } from './hooks/useSession';
import { useChat } from './hooks/useChat';
import { BirthDetailsForm } from './components/BirthDetailsForm';
import { ChatInterface } from './components/ChatInterface';
import { Compass, Sparkles, Loader2 } from 'lucide-react';
import { BirthData } from './types';

export const App: React.FC = () => {
  const {
    sessionId,
    birthData,
    history,
    loading: sessionLoading,
    error: sessionError,
    updateBirthData,
    addMessageToHistory,
    resetSession,
  } = useSession();

  const {
    sendMessage,
    streaming,
    toolActivities,
    currentStreamedContent,
  } = useChat(sessionId);

  const handleBirthDetailsSubmit = async (data: BirthData) => {
    // 1. Update birth data locally to trigger switching layout
    updateBirthData(data);

    // 2. Trigger initial backend geocode & birth chart calculation
    const initPrompt = `Compute my birth chart and provide an overview of my astrological identity. Birth info: Name: ${data.name}, Date: ${data.date}, Time: ${data.time_unknown ? 'Unknown' : data.time}, Place: ${data.place}.`;
    
    // Add a beautiful user-facing placeholder message in the logs
    addMessageToHistory({
      id: `user_init_${Date.now()}`,
      role: 'user',
      content: `Calculating my birth chart for ${data.name} (born ${data.date} at ${data.place}).`
    });

    // Send chat command and pass birth data payload to save it to DB
    await sendMessage(initPrompt, data, true, (fullMessage) => {
      addMessageToHistory({
        id: `ai_init_${Date.now()}`,
        role: 'assistant',
        content: fullMessage
      });
    });
  };

  const handleSendMessage = async (text: string) => {
    // Add user message to local history log
    addMessageToHistory({
      id: `user_${Date.now()}`,
      role: 'user',
      content: text
    });

    // Send message to agent
    await sendMessage(text, birthData, false, (fullMessage) => {
      addMessageToHistory({
        id: `ai_${Date.now()}`,
        role: 'assistant',
        content: fullMessage
      });
    });
  };

  if (sessionLoading) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-[#0a0e1a] text-slate-200">
        <Loader2 className="w-10 h-10 text-cosmic-gold animate-spin mb-4" />
        <p className="text-sm font-serif italic text-cosmic-lavender">Consulting celestial alignments...</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-cosmic-gradient relative overflow-hidden">
      {/* Background Star Particles */}
      <div className="absolute inset-0 pointer-events-none opacity-20 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIxIiBmaWxsPSIjZmZmIi8+PC9zdmc+')] bg-repeat" />

      {/* Main Header */}
      <header className="flex-shrink-0 flex items-center justify-between px-6 py-4 bg-cosmic-dark/40 border-b border-cosmic-lavender/10 backdrop-blur-sm z-10">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-cosmic-gold/10 border border-cosmic-gold/30 text-cosmic-gold shadow-gold-glow">
            <Compass className="w-5 h-5" />
          </div>
          <span className="text-xl font-serif text-slate-100 tracking-wider">
            Aradhana <span className="text-cosmic-gold">AstroAgent</span>
          </span>
        </div>
        <div className="flex items-center space-x-1.5 text-xs text-cosmic-lavender font-serif italic">
          <Sparkles className="w-3.5 h-3.5 text-cosmic-gold animate-pulse" />
          <span>Daily Spiritual Companion</span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden p-4 md:p-6 flex items-center justify-center z-10">
        {sessionError && (
          <div className="absolute top-6 left-1/2 transform -translate-x-1/2 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs px-4 py-2.5 rounded-xl shadow-md backdrop-blur-md">
            ⚠️ {sessionError}
          </div>
        )}

        {birthData === null ? (
          <BirthDetailsForm onSubmit={handleBirthDetailsSubmit} initialData={birthData} />
        ) : (
          <div className="w-full max-w-5xl h-full flex flex-col">
            <ChatInterface
              messages={history}
              birthData={birthData}
              streaming={streaming}
              toolActivities={toolActivities}
              currentStreamedContent={currentStreamedContent}
              onSendMessage={handleSendMessage}
              onResetSession={resetSession}
            />
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
