import DOMPurify from 'dompurify';

/**
 * Sanitizes dangerous HTML content while preserving basic layout tags (b, i, strong, em, br, p).
 */
export const sanitizeHTML = (html: string): string => {
  if (!html) return '';
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'li', 'ol', 'span',
      'table', 'thead', 'tbody', 'tr', 'th', 'td', 'hr', 'div',
      'h1', 'h2', 'h3', 'h4',
    ],
    ALLOWED_ATTR: ['href', 'target', 'class'],
    USE_PROFILES: { html: true }
  });
};

/**
 * Escapes raw strings into HTML-safe formats.
 */
export const escapeHTML = (text: string): string => {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
};
