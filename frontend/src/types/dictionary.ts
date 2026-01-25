export interface DictionaryField {
  name: string;
  dataset: string;
  dataset_id?: string;
  data_type: string;
  description?: string;
  is_pii: boolean;
  nullable: boolean;
  is_primary_key: boolean;
  is_foreign_key: boolean;
  foreign_key_reference?: string;
  example_value?: string;
  constraints?: Array<{ type: string; value: unknown; message?: string }>;
  publisher_team: string;
}

export interface DictionarySummary {
  total_datasets: number;
  total_fields: number;
  total_teams: number;
  pii_field_count: number;
}

export interface DictionaryDataset {
  id?: string;
  name: string;
  description?: string;
  publisher_team: string;
  publisher_owner?: string;
  status: string;
  version: string;
  subscriber_count: number;
  field_count?: number;
  tags?: string[];
}

export interface Dictionary {
  datasets: DictionaryDataset[];
  fields: DictionaryField[];
  teams: string[];
  pii_fields: DictionaryField[];
  summary: DictionarySummary;
}

export interface ERDNodeField {
  name: string;
  data_type: string;
  is_primary_key: boolean;
  is_foreign_key: boolean;
  is_pii: boolean;
  nullable: boolean;
}

export interface ERDNode {
  id: string;
  type: string;
  label: string;
  publisher_team?: string;
  publisher_owner?: string;
  status?: string;
  version?: string;
  description?: string;
  fields: ERDNodeField[];
}

export interface ERDEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  label?: string;
  use_case?: string;
}

export interface ERDData {
  nodes: ERDNode[];
  edges: ERDEdge[];
  metadata?: {
    total_nodes: number;
    total_edges: number;
    team_filter?: string;
  };
}
