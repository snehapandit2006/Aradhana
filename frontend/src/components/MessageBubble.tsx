import React from 'react';
import { Message } from '../types';
import { sanitizeHTML } from '../utils/sanitize';
import { Sparkles, User } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  // Enhanced markdown-to-HTML parser for rich chart content
  const renderContent = (text: string) => {
    // Split into lines for block-level processing
    const lines = text.split('\n');
    const outputLines: string[] = [];
    let inTable = false;
    let tableRows: string[] = [];

    const escapeHtml = (s: string) =>
      s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Inline formatting (bold, italic)
    const inlineFormat = (s: string) => {
      let out = escapeHtml(s);
      out = out.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>');
      out = out.replace(/\*(.*?)\*/g, '<em class="italic text-cosmic-gold">$1</em>');
      return out;
    };

    const flushTable = () => {
      if (tableRows.length === 0) return;
      // First row = header, second row = separator (skip), rest = body
      const headerCells = tableRows[0].split('|').map(c => c.trim()).filter(Boolean);
      const bodyRows = tableRows.slice(2); // skip separator row
      let tableHtml = '<div class="overflow-x-auto my-2"><table class="w-full text-xs border-collapse">';
      tableHtml += '<thead><tr>';
      headerCells.forEach(cell => {
        tableHtml += `<th class="border border-cosmic-lavender/20 px-2 py-1 text-cosmic-gold text-left">${inlineFormat(cell)}</th>`;
      });
      tableHtml += '</tr></thead><tbody>';
      bodyRows.forEach(row => {
        const cells = row.split('|').map(c => c.trim()).filter(Boolean);
        tableHtml += '<tr>';
        cells.forEach(cell => {
          tableHtml += `<td class="border border-cosmic-lavender/20 px-2 py-1">${inlineFormat(cell)}</td>`;
        });
        tableHtml += '</tr>';
      });
      tableHtml += '</tbody></table></div>';
      outputLines.push(tableHtml);
      tableRows = [];
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Detect markdown tables (lines containing |)
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        inTable = true;
        tableRows.push(trimmed);
        continue;
      } else if (inTable) {
        flushTable();
        inTable = false;
      }

      // Headers
      if (trimmed.startsWith('### ')) {
        outputLines.push(`<p class="text-sm font-semibold text-cosmic-gold mt-3 mb-1">${inlineFormat(trimmed.slice(4))}</p>`);
      } else if (trimmed.startsWith('## ')) {
        outputLines.push(`<p class="text-base font-semibold text-cosmic-gold mt-3 mb-1">${inlineFormat(trimmed.slice(3))}</p>`);
      } else if (trimmed.startsWith('# ')) {
        outputLines.push(`<p class="text-lg font-bold text-cosmic-gold mt-3 mb-1">${inlineFormat(trimmed.slice(2))}</p>`);
      }
      // Horizontal rule
      else if (/^[-*_]{3,}$/.test(trimmed)) {
        outputLines.push('<hr class="border-cosmic-lavender/20 my-2" />');
      }
      // Unordered list items
      else if (/^[-*] /.test(trimmed)) {
        outputLines.push(`<li class="ml-4 list-disc">${inlineFormat(trimmed.slice(2))}</li>`);
      }
      // Ordered list items
      else if (/^\d+\.\s/.test(trimmed)) {
        const content = trimmed.replace(/^\d+\.\s/, '');
        outputLines.push(`<li class="ml-4 list-decimal">${inlineFormat(content)}</li>`);
      }
      // Empty line = paragraph break
      else if (trimmed === '') {
        outputLines.push('<br />');
      }
      // Normal text
      else {
        outputLines.push(inlineFormat(trimmed) + '<br />');
      }
    }

    // Flush any remaining table
    if (inTable) flushTable();

    const html = outputLines.join('\n');
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
