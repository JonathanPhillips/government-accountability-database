// API Response Types
export interface PaginatedResponse<T> {
  total: number;
  skip: number;
  limit: number;
  items: T[];
}

// Enums
export type SeverityType = 'low' | 'medium' | 'high' | 'critical';
export type VerificationStatus = 'unverified' | 'alleged' | 'documented' | 'disproven';
export type GeographicScope = 'federal' | 'state' | 'local' | 'international';
export type ActorType = 'agency' | 'official' | 'contractor' | 'military' | 'law_enforcement';
export type ActorRole = 'perpetrator' | 'complicit' | 'enabler' | 'observer';
export type SourceType = 'court_filing' | 'government_report' | 'news_primary' | 'news_secondary' | 'video' | 'audio' | 'ngo_report' | 'academic' | 'social_media' | 'leaked_document';
export type ReliabilityLevel = 'primary' | 'secondary' | 'tertiary';
export type ViolationType = 'alleged' | 'documented' | 'adjudicated';
export type FrameworkType = 'constitutional' | 'statutory' | 'treaty' | 'court_order' | 'regulation';

// Core Entities
export interface Category {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Actor {
  id: string;
  name: string;
  actor_type: ActorType;
  parent_actor_id: string | null;
  description: string | null;
  wikipedia_url: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Target {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface LegalFramework {
  id: string;
  name: string;
  framework_type: FrameworkType;
  citation: string | null;
  description: string | null;
  url: string | null;
  created_at: string;
  updated_at: string;
}

export interface Pattern {
  id: string;
  name: string;
  description: string | null;
  historical_precedent: string | null;
  created_at: string;
  updated_at: string;
}

export interface Source {
  id: string;
  incident_id: string;
  source_type: SourceType;
  title: string;
  url: string | null;
  publication_date: string | null;
  publisher: string | null;
  author: string | null;
  reliability: ReliabilityLevel;
  archived_url: string | null;
  archived_locally: boolean;
  local_file_path: string | null;
  excerpt: string | null;
  created_at: string;
  updated_at: string;
}

// Incident Types
export interface IncidentListItem {
  id: string;
  title: string;
  date_occurred: string;
  date_range_end: string | null;
  summary: string;
  category_id: string;
  subcategory: string | null;
  severity: SeverityType;
  verification_status: VerificationStatus;
  geographic_scope: GeographicScope;
  location_state: string | null;
  location_city: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
  source_count: number;
}

export interface IncidentActor {
  actor: Actor;
  role: ActorRole;
}

export interface IncidentLegalFramework {
  legal_framework: LegalFramework;
  violation_type: ViolationType;
}

export interface IncidentDetail extends IncidentListItem {
  detailed_description: string | null;
  sources: Source[];
  actors: IncidentActor[];
  persons: any[]; // Person type not fully defined yet
  targets: Target[];
  legal_frameworks: IncidentLegalFramework[];
  patterns: Pattern[];
}

// Filter Types
export interface IncidentFilters {
  category_id?: string;
  actor_id?: string;
  severity?: SeverityType;
  verification_status?: string;
  geographic_scope?: string;
  location_state?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
  skip?: number;
  limit?: number;
}
