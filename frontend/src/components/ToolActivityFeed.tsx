import React, { useState } from 'react';
import { ToolActivity } from '../types';
import { ChevronDown, ChevronUp, Loader2, CheckCircle2, XCircle, Compass } from 'lucide-react';

interface ToolActivityFeedProps {
  activities: ToolActivity[];
}

export const ToolActivityFeed: React.FC<ToolActivityFeedProps> = ({ activities }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (activities.length === 0) return null;

  // Map tool keys to user-friendly messages
  const getToolDisplayName = (name: string) => {
    switch (name) {
      case 'geocode_place':
        return 'Resolving birth coordinates...';
      case 'compute_birth_chart':
        return 'Calculating natal planetary alignment...';
      case 'get_daily_transits':
        return 'Analyzing daily planetary transits...';
      case 'knowledge_lookup':
        return 'Retrieving astrological texts...';
      default:
        return `Executing ${name}...`;
    }
  };

  return (
    <div className="mb-4 bg-cosmic-slate/50 border border-cosmic-gold/20 rounded-xl overflow-hidden shadow-gold-glow max-w-lg">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-xs font-serif tracking-wider text-cosmic-gold bg-cosmic-slate/80 hover:bg-cosmic-slate transition"
      >
        <div className="flex items-center space-x-2">
          <Compass className="w-3.5 h-3.5 animate-spin" style={{ animationDuration: '6s' }} />
          <span>ASTROLOGICAL TOOL CHAIN</span>
          <span className="bg-cosmic-gold/20 text-[10px] px-1.5 py-0.5 rounded-full font-sans">
            {activities.length}
          </span>
        </div>
        {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>

      {isOpen && (
        <div className="p-3 space-y-2 border-t border-cosmic-gold/10 text-xs font-sans">
          {activities.map((act, index) => (
            <div key={index} className="flex items-start justify-between space-x-3 py-1">
              <div className="flex items-start space-x-2.5">
                {act.status === 'pending' && (
                  <Loader2 className="w-4.5 h-4.5 text-cosmic-gold animate-spin mt-0.5" />
                )}
                {act.status === 'success' && (
                  <CheckCircle2 className="w-4.5 h-4.5 text-emerald-400 mt-0.5" />
                )}
                {act.status === 'failed' && (
                  <XCircle className="w-4.5 h-4.5 text-rose-400 mt-0.5" />
                )}
                
                <div>
                  <p className="text-slate-200 font-medium">{getToolDisplayName(act.tool)}</p>
                  {act.arguments && (
                    <p className="text-[10px] text-slate-400 mt-0.5 italic">
                      Args: {JSON.stringify(act.arguments)}
                    </p>
                  )}
                </div>
              </div>
              
              <div className="text-[10px]">
                {act.status === 'pending' && <span className="text-cosmic-gold">Calculating...</span>}
                {act.status === 'success' && <span className="text-emerald-400">✓ Complete</span>}
                {act.status === 'failed' && <span className="text-rose-400">✗ Failed</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
