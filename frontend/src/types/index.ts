export interface Citation {
  source: string;
  section: string;
  snippet: string;
}

export interface CriticVerdict {
  faithfulness_score?: number;
  hallucination_detected?: boolean;
  notes?: string;
  verdict?: string;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  agent_chosen: string;
  category: string;
  urgency: string;
  classification_confidence: number;
  citations: Citation[];
  pending_action?: PendingAction | null;
  retrieved_chunks?: Array<Record<string, unknown>>;
  critic_verdict?: CriticVerdict | null;
  pii_types_detected: string[];
  trace_id: string;
  latency_ms: number;
  estimated_cost_usd: number;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  data?: Partial<ChatResponse>;
}

export interface PendingAction {
  action_id: string;
  session_id: string;
  action_type: string;
  status: string; // 'pending_approval' | 'approved' | 'rejected' | 'completed'
  requires_approval: boolean;
  payload: Record<string, unknown>;
  created_at: string;
  resolved_at?: string | null;
}

export interface Order {
  order_id: string;
  customer_name: string;
  email: string;
  product_title: string;
  price_usd: number;
  status: string;
  order_date: string;
  expected_delivery: string;
  carrier: string;
}

export interface Ticket {
  ticket_id: string;
  session_id: string;
  customer_email?: string | null;
  category: string;
  urgency: string;
  status: string;
  subject: string;
  description: string;
  created_at: string;
}

export interface ClassifyResult {
  category: string;
  urgency: string;
  confidence: number;
  probabilities: Record<string, number>;
}

export interface TraceRecord {
  trace_id: string;
  session_id: string;
  timestamp: string;
  pathway: string;
  latency_ms: number;
  estimated_cost_usd: number;
  critic_score?: number;
  details?: Record<string, unknown>;
}

export interface EvalRecord {
  Configuration: string;
  'Hit-Rate@4': string;
  MRR: string;
  'Answer Correctness': string;
  'Latency (p50 ms)': string;
  'Latency (p95 ms)': string;
  'Cost ($/1000q)': string;
  'Key Innovation': string;
}
