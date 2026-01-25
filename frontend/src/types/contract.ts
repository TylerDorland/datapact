export interface Publisher {
  team: string;
  owner: string;
  repository_url?: string;
  contact_email?: string;
}

export interface FieldConstraint {
  type: string;
  value: string | number;
  message?: string;
}

export interface ContractField {
  id: string;
  name: string;
  data_type: DataType;
  description?: string;
  nullable: boolean;
  is_pii: boolean;
  is_primary_key: boolean;
  is_foreign_key: boolean;
  foreign_key_reference?: string;
  example_value?: string;
  constraints: FieldConstraint[];
}

export interface QualityMetric {
  id: string;
  metric_type: MetricType;
  threshold: string;
  measurement_method?: string;
  alert_on_breach: boolean;
}

export interface AccessConfig {
  endpoint_url: string;
  methods: string[];
  auth_type: AuthType;
  required_scopes: string[];
  rate_limit?: string;
}

export interface Subscriber {
  id: string;
  team: string;
  use_case?: string;
  fields_used: string[];
  contact_email?: string;
  subscribed_at: string;
}

export interface Contract {
  id: string;
  name: string;
  version: string;
  description?: string;
  status: ContractStatus;
  publisher_team: string;
  publisher_owner: string;
  repository_url?: string;
  contact_email?: string;
  fields: ContractField[];
  quality_metrics: QualityMetric[];
  access?: AccessConfig;
  subscribers: Subscriber[];
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface ContractVersion {
  id: string;
  version: string;
  change_summary?: string;
  changed_by?: string;
  created_at: string;
}

export type DataType =
  | 'string'
  | 'integer'
  | 'float'
  | 'decimal'
  | 'boolean'
  | 'date'
  | 'datetime'
  | 'timestamp'
  | 'uuid'
  | 'json'
  | 'array';

export type MetricType =
  | 'freshness'
  | 'completeness'
  | 'accuracy'
  | 'availability'
  | 'uniqueness';

export type AuthType = 'none' | 'api_key' | 'oauth2' | 'basic' | 'jwt';

export type ContractStatus = 'active' | 'deprecated' | 'draft';
