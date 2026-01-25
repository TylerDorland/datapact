export interface Notification {
  id: string;
  event_type: string;
  event_id?: string;
  contract_id?: string;
  contract_name?: string;
  recipient_email: string;
  recipient_team?: string;
  subject: string;
  status: NotificationStatus;
  channel: string;
  sent_at?: string;
  read_at?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface NotificationPreference {
  id: string;
  email: string;
  team?: string;
  email_enabled: boolean;
  slack_enabled: boolean;
  schema_drift_enabled: boolean;
  quality_breach_enabled: boolean;
  pr_blocked_enabled: boolean;
  contract_updated_enabled: boolean;
  deprecation_warning_enabled: boolean;
  digest_enabled: boolean;
  digest_frequency: string;
  created_at: string;
  updated_at: string;
}

export interface Watcher {
  id: string;
  contract_id?: string;
  contract_name?: string;
  publisher_team?: string;
  tag?: string;
  watcher_email: string;
  watcher_team?: string;
  watch_schema_drift: boolean;
  watch_quality_breach: boolean;
  watch_contract_updated: boolean;
  watch_deprecation: boolean;
  watch_pr_blocked: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type AlertType =
  | 'schema_drift'
  | 'quality_breach'
  | 'availability_failure'
  | 'pr_blocked'
  | 'contract_updated'
  | 'deprecation_warning';

export type NotificationStatus = 'pending' | 'sending' | 'sent' | 'failed' | 'skipped';
