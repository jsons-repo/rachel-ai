

export enum FlagSource {
  SHALLOW = 'shallow',
  DEEP = 'deep',
  USER = 'user',
}

export enum FlagCategory {
  PERSON = 'person',
  PLACE = 'place',
  CLAIM = 'claim',
  ORG = 'org',
  EVENT = 'event',
}

export enum ExitReason {
  NONE = 'none',
  DUPLICATE = 'duplicate',
  CONFUSING = 'confusing',
  INSUBSTANTIAL = 'insubstantial',
}

export enum SegmentStatus {
  IN_PROGRESS = 'in_progress',
  FLAGGED = 'flagged',
  COMPLETE = 'complete',
}


export const ExitReasonLabels: Record<ExitReason, string> = {
  [ExitReason.NONE]: "No issue detected",
  [ExitReason.DUPLICATE]: "Duplicate of previous statement",
  [ExitReason.CONFUSING]: "Too vague or ambiguous",
  [ExitReason.INSUBSTANTIAL]: "Not enough context to say anything meaningful",
};

export interface DeepSearchResponse {
  topic: string;
  summary: string;
  key_figures: string[];
  timeline: string[];
  controversy: string;
  evidence: string;
  query_duration: number;
}

export type Flag = {
  id: string;
  matches: string[];
  severity: number;
  source: FlagSource;
  summary?: string;
  text?: string;
  category?: string;
  source_prompt?: string;
  exit_reason?: ExitReason;
  deep_search?: string;
};

export type Segment = {
  id: string;
  transcript: string;
  start: number;
  end: number;
  created_at: number;
  pipeline_started_at: number;
  latency?: number;
  duration?: number;
  flags?: Flag[];
  source?: string;
  status?: SegmentStatus;
  last_updated: number;
};

export type MetricData = {
  cpu: number;
  ram: number;
  gpu?: number;
  segments_processed: number;
  queues: {
    transcript: number;
    shallow_results: number;
    deep_queue: number;
    deep_results: number;
  };
  timestamp: number;
};

export type VoiceSignalPayload = {
  isSpeaking: boolean;
  volume: number; // normalized 0.0–1.0
};