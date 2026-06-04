import React from 'react';
import { Message } from '../types';
import { sanitizeHTML } from '../utils/sanitize';
import { Sparkles, User } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  // Basic inline markdown-to-HTML parser (bold, italics, line breaks)
  const renderContent = (text: string) => {
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Replace **text** with <strong>text</strong>
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>');
    
    // Replace *text* with <em>text</em>
    html = html.replace(/\*(.*?)\*/g, '<em class="italic text-cosmic-gold">$1</em>');
    
    // Replace linebreaks with br
    html = html.replace(/\n/g, '<br />');

    const cleanHtml = sanitizeHTML(html);
    return <div dangerouslySetInnerHTML={{ __html: cleanHtml }} />;
  };

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex max-w-[80%] items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border ${
          isUser 
            ? 'bg-cosmic-gold/10 border-cosmic-gold/40 text-cosmic-gold' 
            : 'bg-cosmic-lavender/10 border-cosmic-lavender/40 text-cosmic-lavender'
        }`}>
          {isUser ? <User className="w-4.5 h-4.5" /> : <Sparkles className="w-4.5 h-4.5" />}
        </div>

        {/* Text Container */}
        <div className={`flex flex-col`}>
          <span className={`text-[10px] uppercase tracking-wider mb-1 ${isUser ? 'text-cosmic-gold text-right' : 'text-cosmic-lavender text-left'}`}>
            {isUser ? 'Seeker' : 'AstroAgent'}
          </span>
          <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed border ${
            isUser
              ? 'bg-cosmic-gold/5 text-cosmic-gold border-cosmic-gold/20 rounded-tr-none shadow-gold-glow'
              : 'bg-cosmic-lavender/5 text-slate-200 border-cosmic-lavender/20 rounded-tl-none shadow-lavender-glow'
          }`}>
            {renderContent(message.content)}
          </div>
        </div>
      </div>
    </div>
  );
};
