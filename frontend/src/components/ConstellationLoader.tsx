import React from 'react';

export const ConstellationLoader: React.FC = () => {
  return (
    <div className="flex items-center justify-center space-x-2 py-4 px-6 bg-cosmic-slate/40 border border-cosmic-lavender/20 rounded-2xl w-fit shadow-lavender-glow">
      {/* Represent a small constellation with staggered delays */}
      <span className="text-xs text-cosmic-lavender font-serif italic mr-2">Consulting the cosmos</span>
      <div className="flex space-x-1.5 items-center">
        <div className="w-2 h-2 rounded-full bg-cosmic-gold pulsing-star" style={{ animationDelay: '0s' }}></div>
        <div className="w-1.5 h-1.5 rounded-full bg-cosmic-lavender pulsing-star" style={{ animationDelay: '0.4s' }}></div>
        <div className="w-2 h-2 rounded-full bg-cosmic-gold pulsing-star" style={{ animationDelay: '0.8s' }}></div>
        <div className="w-1.5 h-1.5 rounded-full bg-cosmic-lavender pulsing-star" style={{ animationDelay: '1.2s' }}></div>
        <div className="w-2.5 h-2.5 rounded-full bg-cosmic-gold pulsing-star" style={{ animationDelay: '1.6s' }}></div>
      </div>
    </div>
  );
};
