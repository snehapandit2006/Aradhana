export interface BirthData {
  name: string;
  date: string;
  time?: string;
  time_unknown: boolean;
  place: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
}

export interface ToolActivity {
  tool: string;
  arguments: any;
  status: 'pending' | 'success' | 'failed';
  error?: string;
  output_summary?: string;
}

export interface ChatSessionState {
  session_id: string;
  birth_data: BirthData | null;
  history: Message[];
  loading: boolean;
  error: string | null;
}
