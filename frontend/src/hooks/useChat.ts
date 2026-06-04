import { useState, useCallback } from 'react';
import { BirthData, ToolActivity } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useChat = (sessionId: string) => {
  const [streaming, setStreaming] = useState<boolean>(false);
  const [toolActivities, setToolActivities] = useState<ToolActivity[]>([]);
  const [currentStreamedContent, setCurrentStreamedContent] = useState<string>('');

  const sendMessage = useCallback(async (
    message: string,
    birthData: BirthData | null,
    submitBirthData: boolean,
    onMessageComplete: (fullMessage: string) => void
  ) => {
    if (!sessionId) return;

    setStreaming(true);
    setCurrentStreamedContent('');
    setToolActivities([]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message,
          birth_data: submitBirthData ? birthData : null,
        }),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || 'The connection to the stars was interrupted.');
      }

      if (!response.body) {
        throw new Error('No response stream received from the cosmos.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let accumulatedResponse = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process completed lines from SSE stream
        let lineEndIndex;
        while ((lineEndIndex = buffer.indexOf('\n')) !== -1) {
          const line = buffer.slice(0, lineEndIndex).trim();
          buffer = buffer.slice(lineEndIndex + 1);

          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6).trim();

            if (dataStr === '[DONE]') {
              break;
            }

            try {
              const parsed = JSON.parse(dataStr);

              // 1. Text token chunk
              if (parsed.token) {
                accumulatedResponse += parsed.token;
                setCurrentStreamedContent(accumulatedResponse);
              } 
              // 2. Tool started executing
              else if (parsed.tool_start) {
                const toolName = parsed.tool_start;
                setToolActivities((prev) => [
                  ...prev,
                  {
                    tool: toolName,
                    arguments: parsed.arguments,
                    status: 'pending',
                  },
                ]);
              } 
              // 3. Tool completed execution
              else if (parsed.tool_end) {
                const toolName = parsed.tool_end;
                setToolActivities((prev) =>
                  prev.map((act) =>
                    act.tool === toolName && act.status === 'pending'
                      ? {
                          ...act,
                          status: 'success',
                          output_summary:
                            typeof parsed.output === 'object'
                              ? JSON.stringify(parsed.output)
                              : String(parsed.output),
                        }
                      : act
                  )
                );
              }
              // 4. API returned an error
              else if (parsed.error) {
                throw new Error(parsed.error);
              }
            } catch (err) {
              // Ignore partial parse failures
            }
          }
        }
      }

      // Stream fully read, invoke complete callback
      onMessageComplete(accumulatedResponse);

    } catch (error: any) {
      console.error(error);
      const errorMsg = error.message || 'The stars are quiet right now — please try again.';
      onMessageComplete(errorMsg);
    } finally {
      setStreaming(false);
      setCurrentStreamedContent('');
    }
  }, [sessionId]);

  return {
    sendMessage,
    streaming,
    toolActivities,
    currentStreamedContent,
  };
};
