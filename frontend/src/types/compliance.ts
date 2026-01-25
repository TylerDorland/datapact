export interface ComplianceCheck {
  id: string;
  contract_id: string;
  contract_name: string;
  check_type: CheckType;
  status: CheckStatus;
  details: Record<string, unknown>;
  error_message?: string;
  checked_at: string;
}

export interface ComplianceSummary {
  contract_id: string;
  contract_name: string;
  overall_status: CheckStatus;
  last_check: string;
  checks: {
    schema: CheckStatus;
    freshness: CheckStatus;
    completeness: CheckStatus;
    availability: CheckStatus;
  };
  error_count: number;
  warning_count: number;
}

export type CheckType =
  | 'schema'
  | 'freshness'
  | 'completeness'
  | 'accuracy'
  | 'availability';

export type CheckStatus = 'pass' | 'fail' | 'warning' | 'unknown';
