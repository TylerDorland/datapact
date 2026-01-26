# DataPact Frontend

## Overview

A React-based dashboard for visualizing and managing the DataPact platform. The frontend provides:

1. **Data Dictionary** — Browse and search all fields across contracts
2. **Contract Management** — View, create, and edit contracts
3. **Compliance Dashboard** — Monitor contract compliance status
4. **ERD Visualization** — Interactive entity relationship diagrams
5. **Notification Center** — View notification history and manage preferences

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| TypeScript | Type safety |
| Vite | Build tool |
| React Router | Navigation |
| TanStack Query | Data fetching & caching |
| Tailwind CSS | Styling |
| shadcn/ui | Component library |
| Recharts | Charts and graphs |
| React Flow | ERD visualization |
| React Hook Form | Form handling |
| Zod | Schema validation |

---

## Project Structure

```
frontend/
├── Dockerfile
├── nginx.conf
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── .env.example
│
├── public/
│   └── favicon.svg
│
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    │
    ├── api/
    │   ├── client.ts              # Axios instance
    │   ├── contracts.ts           # Contract API calls
    │   ├── dictionary.ts          # Dictionary API calls
    │   ├── compliance.ts          # Compliance API calls
    │   └── notifications.ts       # Notification API calls
    │
    ├── components/
    │   ├── ui/                    # shadcn/ui components
    │   │   ├── button.tsx
    │   │   ├── card.tsx
    │   │   ├── input.tsx
    │   │   ├── table.tsx
    │   │   ├── badge.tsx
    │   │   ├── dialog.tsx
    │   │   ├── dropdown-menu.tsx
    │   │   ├── tabs.tsx
    │   │   ├── toast.tsx
    │   │   └── ...
    │   │
    │   ├── layout/
    │   │   ├── Layout.tsx
    │   │   ├── Sidebar.tsx
    │   │   ├── Header.tsx
    │   │   └── Breadcrumbs.tsx
    │   │
    │   ├── contracts/
    │   │   ├── ContractCard.tsx
    │   │   ├── ContractList.tsx
    │   │   ├── ContractDetail.tsx
    │   │   ├── ContractForm.tsx
    │   │   ├── FieldsTable.tsx
    │   │   ├── QualityMetrics.tsx
    │   │   ├── SubscribersList.tsx
    │   │   └── VersionHistory.tsx
    │   │
    │   ├── dictionary/
    │   │   ├── FieldSearch.tsx
    │   │   ├── FieldTable.tsx
    │   │   ├── FieldDetail.tsx
    │   │   └── PIIBadge.tsx
    │   │
    │   ├── compliance/
    │   │   ├── ComplianceOverview.tsx
    │   │   ├── ComplianceCard.tsx
    │   │   ├── ComplianceHistory.tsx
    │   │   ├── StatusBadge.tsx
    │   │   └── QualityChart.tsx
    │   │
    │   ├── erd/
    │   │   ├── ERDCanvas.tsx
    │   │   ├── DatasetNode.tsx
    │   │   ├── RelationshipEdge.tsx
    │   │   └── ERDControls.tsx
    │   │
    │   └── notifications/
    │       ├── NotificationList.tsx
    │       ├── NotificationItem.tsx
    │       ├── PreferencesForm.tsx
    │       └── WatcherManager.tsx
    │
    ├── hooks/
    │   ├── useContracts.ts
    │   ├── useDictionary.ts
    │   ├── useCompliance.ts
    │   ├── useNotifications.ts
    │   └── useDebounce.ts
    │
    ├── pages/
    │   ├── Dashboard.tsx
    │   ├── Contracts.tsx
    │   ├── ContractDetail.tsx
    │   ├── ContractCreate.tsx
    │   ├── Dictionary.tsx
    │   ├── Compliance.tsx
    │   ├── ERD.tsx
    │   ├── Notifications.tsx
    │   └── Settings.tsx
    │
    ├── types/
    │   ├── contract.ts
    │   ├── field.ts
    │   ├── compliance.ts
    │   └── notification.ts
    │
    └── lib/
        ├── utils.ts
        └── constants.ts
```

---

## Type Definitions

```typescript
// src/types/contract.ts

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
  notification_preferences: NotificationPreferences;
  subscribed_at: string;
}

export interface Contract {
  id: string;
  name: string;
  version: string;
  description?: string;
  status: ContractStatus;
  publisher: Publisher;
  fields: ContractField[];
  quality: QualityMetric[];
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
  | 'string' | 'integer' | 'float' | 'decimal' | 'boolean'
  | 'date' | 'datetime' | 'timestamp' | 'uuid' | 'json' | 'array';

export type MetricType = 
  | 'freshness' | 'completeness' | 'accuracy' | 'availability' | 'uniqueness';

export type AuthType = 'none' | 'api_key' | 'oauth2' | 'basic' | 'jwt';

export type ContractStatus = 'active' | 'deprecated' | 'draft';

export interface NotificationPreferences {
  on_schema_change: boolean;
  on_quality_breach: boolean;
  on_deprecation: boolean;
  on_availability: boolean;
}
```

```typescript
// src/types/compliance.ts

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

export type CheckType = 'schema' | 'freshness' | 'completeness' | 'accuracy' | 'availability';
export type CheckStatus = 'pass' | 'fail' | 'warning' | 'unknown';
```

```typescript
// src/types/notification.ts

export interface Notification {
  id: string;
  contract_id: string;
  contract_name: string;
  alert_type: AlertType;
  recipient_email: string;
  subject: string;
  status: NotificationStatus;
  sent_at?: string;
  created_at: string;
}

export interface Watcher {
  id: string;
  contract_id?: string;  // null for global watchers
  email: string;
  notify_on: string[];
  created_at: string;
}

export type AlertType = 
  | 'schema_drift' | 'quality_breach' | 'availability_down' | 'availability_restored'
  | 'pr_opened' | 'pr_needs_contract' | 'contract_updated' | 'new_subscriber'
  | 'deprecation_warning' | 'pii_field_added' | 'pii_field_removed';

export type NotificationStatus = 'pending' | 'sent' | 'failed' | 'bounced';
```

---

## API Client

```typescript
// src/api/client.ts

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth (if needed later)
apiClient.interceptors.request.use((config) => {
  // Add auth token if available
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

```typescript
// src/api/contracts.ts

import { apiClient } from './client';
import type { Contract, ContractVersion } from '@/types/contract';

export interface ContractListParams {
  skip?: number;
  limit?: number;
  status?: string;
  publisher_team?: string;
  tag?: string;
}

export interface ContractListResponse {
  contracts: Contract[];
  total: number;
  skip: number;
  limit: number;
}

export const contractsApi = {
  list: async (params: ContractListParams = {}): Promise<ContractListResponse> => {
    const { data } = await apiClient.get('/api/v1/contracts', { params });
    return data;
  },

  get: async (id: string): Promise<Contract> => {
    const { data } = await apiClient.get(`/api/v1/contracts/${id}`);
    return data;
  },

  getByName: async (name: string): Promise<Contract> => {
    const { data } = await apiClient.get(`/api/v1/contracts/name/${name}`);
    return data;
  },

  create: async (contract: Partial<Contract>): Promise<Contract> => {
    const { data } = await apiClient.post('/api/v1/contracts', contract);
    return data;
  },

  update: async (id: string, contract: Partial<Contract>): Promise<Contract> => {
    const { data } = await apiClient.put(`/api/v1/contracts/${id}`, contract);
    return data;
  },

  deprecate: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/contracts/${id}`);
  },

  getVersions: async (id: string): Promise<ContractVersion[]> => {
    const { data } = await apiClient.get(`/api/v1/contracts/${id}/versions`);
    return data.versions;
  },

  subscribe: async (id: string, subscription: {
    team: string;
    use_case?: string;
    fields_used?: string[];
    contact_email?: string;
  }): Promise<void> => {
    await apiClient.post(`/api/v1/contracts/${id}/subscribe`, subscription);
  },
};
```

```typescript
// src/api/dictionary.ts

import { apiClient } from './client';

export interface DictionaryField {
  name: string;
  dataset: string;
  data_type: string;
  description?: string;
  is_pii: boolean;
  nullable: boolean;
  example?: string;
  publisher_team: string;
}

export interface DictionarySummary {
  total_datasets: number;
  total_fields: number;
  total_teams: number;
  pii_field_count: number;
}

export interface Dictionary {
  datasets: Array<{
    name: string;
    description?: string;
    publisher: string;
    owner: string;
    status: string;
    version: string;
    subscriber_count: number;
  }>;
  fields: DictionaryField[];
  teams: string[];
  pii_fields: DictionaryField[];
  summary: DictionarySummary;
}

export interface ERDData {
  nodes: Array<{
    id: string;
    type: string;
    label: string;
    publisher: string;
    fields: string[];
  }>;
  edges: Array<{
    from: string;
    to: string;
    type: string;
    label?: string;
  }>;
}

export const dictionaryApi = {
  getFull: async (): Promise<Dictionary> => {
    const { data } = await apiClient.get('/api/v1/dictionary');
    return data;
  },

  search: async (params: {
    q: string;
    data_type?: string;
    is_pii?: boolean;
  }): Promise<DictionaryField[]> => {
    const { data } = await apiClient.get('/api/v1/dictionary/search', { params });
    return data;
  },

  getERD: async (): Promise<ERDData> => {
    const { data } = await apiClient.get('/api/v1/erd');
    return data;
  },

  getERDMermaid: async (): Promise<string> => {
    const { data } = await apiClient.get('/api/v1/erd/mermaid');
    return data;
  },
};
```

```typescript
// src/api/compliance.ts

import { apiClient } from './client';
import type { ComplianceCheck, ComplianceSummary } from '@/types/compliance';

export const complianceApi = {
  getSummary: async (): Promise<ComplianceSummary[]> => {
    const { data } = await apiClient.get('/api/v1/compliance/summary');
    return data;
  },

  getContractCompliance: async (contractId: string): Promise<ComplianceSummary> => {
    const { data } = await apiClient.get(`/api/v1/contracts/${contractId}/compliance/summary`);
    return data;
  },

  getHistory: async (contractId: string, params?: {
    check_type?: string;
    limit?: number;
  }): Promise<ComplianceCheck[]> => {
    const { data } = await apiClient.get(
      `/api/v1/contracts/${contractId}/compliance`,
      { params }
    );
    return data;
  },

  triggerCheck: async (contractId: string, checkType?: string): Promise<void> => {
    await apiClient.post(`/api/v1/contracts/${contractId}/validate`, {
      check_type: checkType,
    });
  },
};
```

---

## React Query Hooks

```typescript
// src/hooks/useContracts.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractsApi, type ContractListParams } from '@/api/contracts';
import type { Contract } from '@/types/contract';

export function useContracts(params: ContractListParams = {}) {
  return useQuery({
    queryKey: ['contracts', params],
    queryFn: () => contractsApi.list(params),
  });
}

export function useContract(id: string) {
  return useQuery({
    queryKey: ['contracts', id],
    queryFn: () => contractsApi.get(id),
    enabled: !!id,
  });
}

export function useContractVersions(id: string) {
  return useQuery({
    queryKey: ['contracts', id, 'versions'],
    queryFn: () => contractsApi.getVersions(id),
    enabled: !!id,
  });
}

export function useCreateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contract: Partial<Contract>) => contractsApi.create(contract),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

export function useUpdateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, contract }: { id: string; contract: Partial<Contract> }) =>
      contractsApi.update(id, contract),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['contracts', id] });
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

export function useDeprecateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => contractsApi.deprecate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}
```

```typescript
// src/hooks/useDictionary.ts

import { useQuery } from '@tanstack/react-query';
import { dictionaryApi } from '@/api/dictionary';

export function useDictionary() {
  return useQuery({
    queryKey: ['dictionary'],
    queryFn: () => dictionaryApi.getFull(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useDictionarySearch(query: string, filters?: {
  data_type?: string;
  is_pii?: boolean;
}) {
  return useQuery({
    queryKey: ['dictionary', 'search', query, filters],
    queryFn: () => dictionaryApi.search({ q: query, ...filters }),
    enabled: query.length > 0,
  });
}

export function useERD() {
  return useQuery({
    queryKey: ['erd'],
    queryFn: () => dictionaryApi.getERD(),
    staleTime: 5 * 60 * 1000,
  });
}
```

```typescript
// src/hooks/useCompliance.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { complianceApi } from '@/api/compliance';

export function useComplianceSummary() {
  return useQuery({
    queryKey: ['compliance', 'summary'],
    queryFn: () => complianceApi.getSummary(),
    refetchInterval: 60 * 1000, // Refresh every minute
  });
}

export function useContractCompliance(contractId: string) {
  return useQuery({
    queryKey: ['compliance', contractId],
    queryFn: () => complianceApi.getContractCompliance(contractId),
    enabled: !!contractId,
    refetchInterval: 60 * 1000,
  });
}

export function useComplianceHistory(contractId: string, checkType?: string) {
  return useQuery({
    queryKey: ['compliance', contractId, 'history', checkType],
    queryFn: () => complianceApi.getHistory(contractId, { check_type: checkType, limit: 50 }),
    enabled: !!contractId,
  });
}

export function useTriggerComplianceCheck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ contractId, checkType }: { contractId: string; checkType?: string }) =>
      complianceApi.triggerCheck(contractId, checkType),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: ['compliance', contractId] });
    },
  });
}
```

---

## Page Components

### Dashboard

```tsx
// src/pages/Dashboard.tsx

import { Link } from 'react-router-dom';
import { 
  Database, FileText, AlertTriangle, CheckCircle, 
  XCircle, Clock, Users, Shield 
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useDictionary } from '@/hooks/useDictionary';
import { useComplianceSummary } from '@/hooks/useCompliance';
import { useContracts } from '@/hooks/useContracts';
import { ComplianceOverview } from '@/components/compliance/ComplianceOverview';

export default function Dashboard() {
  const { data: dictionary, isLoading: dictLoading } = useDictionary();
  const { data: compliance, isLoading: compLoading } = useComplianceSummary();
  const { data: contracts, isLoading: contractsLoading } = useContracts({ limit: 5 });

  const stats = dictionary?.summary;
  
  const complianceStats = compliance?.reduce(
    (acc, c) => {
      if (c.overall_status === 'pass') acc.passing++;
      else if (c.overall_status === 'fail') acc.failing++;
      else acc.warning++;
      return acc;
    },
    { passing: 0, failing: 0, warning: 0 }
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your data governance platform
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Contracts</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_datasets || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active data contracts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Fields</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_fields || 0}</div>
            <p className="text-xs text-muted-foreground">
              Documented in dictionary
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">PII Fields</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pii_field_count || 0}</div>
            <p className="text-xs text-muted-foreground">
              Sensitive data tracked
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Teams</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_teams || 0}</div>
            <p className="text-xs text-muted-foreground">
              Publishing or subscribing
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Compliance Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-green-200 bg-green-50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-green-800">
              Passing
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-800">
              {complianceStats?.passing || 0}
            </div>
          </CardContent>
        </Card>

        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-yellow-800">
              Warnings
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-800">
              {complianceStats?.warning || 0}
            </div>
          </CardContent>
        </Card>

        <Card className="border-red-200 bg-red-50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-red-800">
              Failing
            </CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-800">
              {complianceStats?.failing || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Contracts & Compliance Issues */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Contracts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {contracts?.contracts.map((contract) => (
                <Link
                  key={contract.id}
                  to={`/contracts/${contract.id}`}
                  className="flex items-center justify-between p-2 rounded-lg hover:bg-muted"
                >
                  <div>
                    <p className="font-medium">{contract.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {contract.publisher.team}
                    </p>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    v{contract.version}
                  </span>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Compliance Issues</CardTitle>
          </CardHeader>
          <CardContent>
            <ComplianceOverview limit={5} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

### Contracts List

```tsx
// src/pages/Contracts.tsx

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ContractCard } from '@/components/contracts/ContractCard';
import { useContracts } from '@/hooks/useContracts';

export default function Contracts() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [teamFilter, setTeamFilter] = useState<string>('all');

  const { data, isLoading } = useContracts({
    status: statusFilter !== 'all' ? statusFilter : undefined,
    publisher_team: teamFilter !== 'all' ? teamFilter : undefined,
    limit: 50,
  });

  const filteredContracts = data?.contracts.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.description?.toLowerCase().includes(search.toLowerCase())
  );

  // Get unique teams for filter
  const teams = [...new Set(data?.contracts.map((c) => c.publisher.team) || [])];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Contracts</h1>
          <p className="text-muted-foreground">
            Manage your data contracts
          </p>
        </div>
        <Button asChild>
          <Link to="/contracts/new">
            <Plus className="mr-2 h-4 w-4" />
            New Contract
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search contracts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="deprecated">Deprecated</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
          </SelectContent>
        </Select>
        <Select value={teamFilter} onValueChange={setTeamFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Team" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Teams</SelectItem>
            {teams.map((team) => (
              <SelectItem key={team} value={team}>
                {team}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Contract Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredContracts?.map((contract) => (
            <ContractCard key={contract.id} contract={contract} />
          ))}
        </div>
      )}

      {filteredContracts?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No contracts found</p>
        </div>
      )}
    </div>
  );
}
```

### Contract Detail

```tsx
// src/pages/ContractDetail.tsx

import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Edit, Trash2, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useContract, useContractVersions } from '@/hooks/useContracts';
import { useContractCompliance, useTriggerComplianceCheck } from '@/hooks/useCompliance';
import { FieldsTable } from '@/components/contracts/FieldsTable';
import { QualityMetrics } from '@/components/contracts/QualityMetrics';
import { SubscribersList } from '@/components/contracts/SubscribersList';
import { VersionHistory } from '@/components/contracts/VersionHistory';
import { ComplianceHistory } from '@/components/compliance/ComplianceHistory';
import { StatusBadge } from '@/components/compliance/StatusBadge';

export default function ContractDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: contract, isLoading } = useContract(id!);
  const { data: compliance } = useContractCompliance(id!);
  const { data: versions } = useContractVersions(id!);
  const triggerCheck = useTriggerComplianceCheck();

  if (isLoading) {
    return <div className="animate-pulse">Loading...</div>;
  }

  if (!contract) {
    return <div>Contract not found</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/contracts">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <h1 className="text-3xl font-bold">{contract.name}</h1>
            <Badge variant={contract.status === 'active' ? 'default' : 'secondary'}>
              {contract.status}
            </Badge>
          </div>
          <p className="text-muted-foreground">{contract.description}</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => triggerCheck.mutate({ contractId: id! })}
            disabled={triggerCheck.isPending}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${triggerCheck.isPending ? 'animate-spin' : ''}`} />
            Run Compliance Check
          </Button>
          <Button variant="outline" asChild>
            <Link to={`/contracts/${id}/edit`}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Link>
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Version</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">v{contract.version}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Publisher</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-medium">{contract.publisher.team}</div>
            <div className="text-sm text-muted-foreground">{contract.publisher.owner}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Subscribers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{contract.subscribers.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Compliance</CardTitle>
          </CardHeader>
          <CardContent>
            {compliance && <StatusBadge status={compliance.overall_status} size="lg" />}
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="schema">
        <TabsList>
          <TabsTrigger value="schema">Schema ({contract.fields.length} fields)</TabsTrigger>
          <TabsTrigger value="quality">Quality SLAs</TabsTrigger>
          <TabsTrigger value="subscribers">Subscribers</TabsTrigger>
          <TabsTrigger value="compliance">Compliance History</TabsTrigger>
          <TabsTrigger value="versions">Version History</TabsTrigger>
        </TabsList>

        <TabsContent value="schema" className="mt-4">
          <FieldsTable fields={contract.fields} />
        </TabsContent>

        <TabsContent value="quality" className="mt-4">
          <QualityMetrics 
            metrics={contract.quality} 
            compliance={compliance}
          />
        </TabsContent>

        <TabsContent value="subscribers" className="mt-4">
          <SubscribersList 
            subscribers={contract.subscribers}
            contractId={contract.id}
          />
        </TabsContent>

        <TabsContent value="compliance" className="mt-4">
          <ComplianceHistory contractId={contract.id} />
        </TabsContent>

        <TabsContent value="versions" className="mt-4">
          <VersionHistory versions={versions || []} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

### Data Dictionary

```tsx
// src/pages/Dictionary.tsx

import { useState } from 'react';
import { Search, Filter, Download } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { FieldTable } from '@/components/dictionary/FieldTable';
import { useDictionary, useDictionarySearch } from '@/hooks/useDictionary';
import { useDebounce } from '@/hooks/useDebounce';

const DATA_TYPES = [
  'string', 'integer', 'float', 'decimal', 'boolean',
  'date', 'datetime', 'timestamp', 'uuid', 'json', 'array'
];

export default function Dictionary() {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [piiOnly, setPiiOnly] = useState(false);

  const debouncedSearch = useDebounce(search, 300);
  
  const { data: dictionary, isLoading: dictLoading } = useDictionary();
  const { data: searchResults, isLoading: searchLoading } = useDictionarySearch(
    debouncedSearch,
    {
      data_type: typeFilter !== 'all' ? typeFilter : undefined,
      is_pii: piiOnly || undefined,
    }
  );

  const fields = debouncedSearch ? searchResults : dictionary?.fields;
  const filteredFields = fields?.filter((f) => {
    if (typeFilter !== 'all' && f.data_type !== typeFilter) return false;
    if (piiOnly && !f.is_pii) return false;
    return true;
  });

  const handleExport = () => {
    const csv = [
      ['Field Name', 'Dataset', 'Type', 'Description', 'PII', 'Nullable'].join(','),
      ...(filteredFields || []).map((f) =>
        [f.name, f.dataset, f.data_type, `"${f.description || ''}"`, f.is_pii, f.nullable].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'data-dictionary.csv';
    a.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Data Dictionary</h1>
          <p className="text-muted-foreground">
            Search and browse all documented fields
          </p>
        </div>
        <Button variant="outline" onClick={handleExport}>
          <Download className="mr-2 h-4 w-4" />
          Export CSV
        </Button>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="relative flex-1 min-w-[300px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search fields by name or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Data Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {DATA_TYPES.map((type) => (
              <SelectItem key={type} value={type}>
                {type}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="flex items-center space-x-2">
          <Switch
            id="pii-filter"
            checked={piiOnly}
            onCheckedChange={setPiiOnly}
          />
          <Label htmlFor="pii-filter">PII Only</Label>
        </div>
      </div>

      {/* Stats */}
      {dictionary?.summary && (
        <div className="flex gap-4 text-sm text-muted-foreground">
          <span>{dictionary.summary.total_fields} total fields</span>
          <span>•</span>
          <span>{dictionary.summary.total_datasets} datasets</span>
          <span>•</span>
          <span>{dictionary.summary.pii_field_count} PII fields</span>
        </div>
      )}

      {/* Results */}
      <FieldTable 
        fields={filteredFields || []} 
        isLoading={dictLoading || searchLoading} 
      />
    </div>
  );
}
```

### ERD Visualization

```tsx
// src/pages/ERD.tsx

import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DatasetNode } from '@/components/erd/DatasetNode';
import { useERD } from '@/hooks/useDictionary';

const nodeTypes = {
  dataset: DatasetNode,
};

export default function ERD() {
  const { data: erdData, isLoading } = useERD();

  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!erdData) return { nodes: [], edges: [] };

    // Position nodes in a grid
    const nodes: Node[] = erdData.nodes.map((node, index) => ({
      id: node.id,
      type: 'dataset',
      position: {
        x: (index % 4) * 300 + 50,
        y: Math.floor(index / 4) * 250 + 50,
      },
      data: {
        label: node.label,
        publisher: node.publisher,
        fields: node.fields,
      },
    }));

    const edges: Edge[] = erdData.edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.from,
      target: edge.to,
      type: edge.type === 'foreign_key' ? 'smoothstep' : 'default',
      animated: edge.type === 'subscription',
      label: edge.label,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
      style: {
        stroke: edge.type === 'foreign_key' ? '#3b82f6' : '#94a3b8',
        strokeWidth: edge.type === 'foreign_key' ? 2 : 1,
      },
    }));

    return { nodes, edges };
  }, [erdData]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  if (isLoading) {
    return (
      <div className="h-[calc(100vh-200px)] flex items-center justify-center">
        <div className="animate-pulse">Loading ERD...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Entity Relationship Diagram</h1>
        <p className="text-muted-foreground">
          Visual representation of data relationships
        </p>
      </div>

      {/* Legend */}
      <div className="flex gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-blue-500" />
          <span>Foreign Key</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-slate-400 border-dashed border-t-2" />
          <span>Subscription</span>
        </div>
      </div>

      {/* ERD Canvas */}
      <Card className="h-[calc(100vh-300px)]">
        <CardContent className="p-0 h-full">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.1}
            maxZoom={2}
          >
            <Controls />
            <Background />
          </ReactFlow>
        </CardContent>
      </Card>
    </div>
  );
}
```

```tsx
// src/components/erd/DatasetNode.tsx

import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Database } from 'lucide-react';

interface DatasetNodeProps {
  data: {
    label: string;
    publisher: string;
    fields: string[];
  };
}

export const DatasetNode = memo(({ data }: DatasetNodeProps) => {
  return (
    <div className="bg-white border-2 border-slate-200 rounded-lg shadow-md min-w-[200px]">
      <Handle type="target" position={Position.Top} className="!bg-blue-500" />
      
      <div className="bg-slate-100 px-3 py-2 rounded-t-lg border-b flex items-center gap-2">
        <Database className="h-4 w-4 text-slate-600" />
        <span className="font-semibold text-sm">{data.label}</span>
      </div>
      
      <div className="p-2">
        <div className="text-xs text-slate-500 mb-2">{data.publisher}</div>
        <div className="space-y-1 max-h-[150px] overflow-y-auto">
          {data.fields.slice(0, 8).map((field) => (
            <div key={field} className="text-xs font-mono text-slate-700">
              {field}
            </div>
          ))}
          {data.fields.length > 8 && (
            <div className="text-xs text-slate-400">
              +{data.fields.length - 8} more
            </div>
          )}
        </div>
      </div>
      
      <Handle type="source" position={Position.Bottom} className="!bg-blue-500" />
    </div>
  );
});

DatasetNode.displayName = 'DatasetNode';
```

### Compliance Dashboard

```tsx
// src/pages/Compliance.tsx

import { useState } from 'react';
import { RefreshCw, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useComplianceSummary } from '@/hooks/useCompliance';
import { ComplianceCard } from '@/components/compliance/ComplianceCard';
import { QualityChart } from '@/components/compliance/QualityChart';

export default function Compliance() {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const { data: compliance, isLoading, refetch } = useComplianceSummary();

  const filtered = compliance?.filter((c) => {
    if (statusFilter === 'all') return true;
    return c.overall_status === statusFilter;
  });

  const stats = compliance?.reduce(
    (acc, c) => {
      acc.total++;
      if (c.overall_status === 'pass') acc.passing++;
      else if (c.overall_status === 'fail') acc.failing++;
      else if (c.overall_status === 'warning') acc.warning++;
      return acc;
    },
    { total: 0, passing: 0, failing: 0, warning: 0 }
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Compliance Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor contract compliance across all services
          </p>
        </div>
        <Button variant="outline" onClick={() => refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Contracts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total || 0}</div>
          </CardContent>
        </Card>
        <Card className="border-green-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              Passing
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.passing || 0}</div>
          </CardContent>
        </Card>
        <Card className="border-yellow-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              Warnings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats?.warning || 0}</div>
          </CardContent>
        </Card>
        <Card className="border-red-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-600" />
              Failing
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats?.failing || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Compliance Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <QualityChart />
        </CardContent>
      </Card>

      {/* Filter */}
      <div className="flex gap-4">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pass">Passing</SelectItem>
            <SelectItem value="warning">Warnings</SelectItem>
            <SelectItem value="fail">Failing</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Compliance Cards */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered?.map((item) => (
            <ComplianceCard key={item.contract_id} compliance={item} />
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Reusable Components

### Contract Card

```tsx
// src/components/contracts/ContractCard.tsx

import { Link } from 'react-router-dom';
import { Users, Database, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Contract } from '@/types/contract';

interface ContractCardProps {
  contract: Contract;
}

export function ContractCard({ contract }: ContractCardProps) {
  const piiCount = contract.fields.filter((f) => f.is_pii).length;

  return (
    <Link to={`/contracts/${contract.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <CardTitle className="text-lg">{contract.name}</CardTitle>
            <Badge variant={contract.status === 'active' ? 'default' : 'secondary'}>
              {contract.status}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground line-clamp-2">
            {contract.description || 'No description'}
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Database className="h-4 w-4" />
              {contract.fields.length} fields
            </div>
            <div className="flex items-center gap-1">
              <Users className="h-4 w-4" />
              {contract.subscribers.length}
            </div>
            {piiCount > 0 && (
              <Badge variant="outline" className="text-orange-600 border-orange-300">
                {piiCount} PII
              </Badge>
            )}
          </div>
          <div className="mt-3 pt-3 border-t flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              {contract.publisher.team}
            </span>
            <span className="text-sm font-mono">v{contract.version}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
```

### Fields Table

```tsx
// src/components/contracts/FieldsTable.tsx

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Shield, Key, Link as LinkIcon } from 'lucide-react';
import type { ContractField } from '@/types/contract';

interface FieldsTableProps {
  fields: ContractField[];
}

export function FieldsTable({ fields }: FieldsTableProps) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Field Name</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Nullable</TableHead>
            <TableHead>Flags</TableHead>
            <TableHead>Example</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {fields.map((field) => (
            <TableRow key={field.id}>
              <TableCell className="font-mono font-medium">
                {field.name}
              </TableCell>
              <TableCell>
                <Badge variant="outline">{field.data_type}</Badge>
              </TableCell>
              <TableCell className="max-w-[300px] truncate">
                {field.description || '-'}
              </TableCell>
              <TableCell>
                {field.nullable ? (
                  <span className="text-muted-foreground">Yes</span>
                ) : (
                  <span className="font-medium">No</span>
                )}
              </TableCell>
              <TableCell>
                <div className="flex gap-1">
                  {field.is_primary_key && (
                    <Badge variant="default" className="gap-1">
                      <Key className="h-3 w-3" />
                      PK
                    </Badge>
                  )}
                  {field.is_foreign_key && (
                    <Badge variant="secondary" className="gap-1">
                      <LinkIcon className="h-3 w-3" />
                      FK
                    </Badge>
                  )}
                  {field.is_pii && (
                    <Badge variant="destructive" className="gap-1">
                      <Shield className="h-3 w-3" />
                      PII
                    </Badge>
                  )}
                </div>
              </TableCell>
              <TableCell className="font-mono text-sm text-muted-foreground">
                {field.example_value || '-'}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
```

### Status Badge

```tsx
// src/components/compliance/StatusBadge.tsx

import { CheckCircle, XCircle, AlertTriangle, HelpCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { CheckStatus } from '@/types/compliance';

interface StatusBadgeProps {
  status: CheckStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const statusConfig = {
  pass: {
    icon: CheckCircle,
    label: 'Passing',
    variant: 'default' as const,
    className: 'bg-green-100 text-green-800 border-green-300',
  },
  fail: {
    icon: XCircle,
    label: 'Failing',
    variant: 'destructive' as const,
    className: 'bg-red-100 text-red-800 border-red-300',
  },
  warning: {
    icon: AlertTriangle,
    label: 'Warning',
    variant: 'secondary' as const,
    className: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  },
  unknown: {
    icon: HelpCircle,
    label: 'Unknown',
    variant: 'outline' as const,
    className: 'bg-gray-100 text-gray-800 border-gray-300',
  },
};

const sizeConfig = {
  sm: 'h-3 w-3',
  md: 'h-4 w-4',
  lg: 'h-5 w-5',
};

export function StatusBadge({ status, size = 'md', showLabel = true }: StatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Badge variant="outline" className={`gap-1 ${config.className}`}>
      <Icon className={sizeConfig[size]} />
      {showLabel && config.label}
    </Badge>
  );
}
```

---

## Application Layout

```tsx
// src/components/layout/Layout.tsx

import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export function Layout() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

```tsx
// src/components/layout/Sidebar.tsx

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Book,
  GitBranch,
  Shield,
  Bell,
  Settings,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/contracts', icon: FileText, label: 'Contracts' },
  { to: '/dictionary', icon: Book, label: 'Dictionary' },
  { to: '/erd', icon: GitBranch, label: 'ERD' },
  { to: '/compliance', icon: Shield, label: 'Compliance' },
  { to: '/notifications', icon: Bell, label: 'Notifications' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r">
      <div className="p-6">
        <h1 className="text-xl font-bold text-primary">DataPact</h1>
        <p className="text-sm text-muted-foreground">Data Governance</p>
      </div>
      <nav className="px-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg mb-1 transition-colors ${
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted'
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
```

---

## App Router Setup

```tsx
// src/App.tsx

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { Layout } from '@/components/layout/Layout';

import Dashboard from '@/pages/Dashboard';
import Contracts from '@/pages/Contracts';
import ContractDetail from '@/pages/ContractDetail';
import ContractCreate from '@/pages/ContractCreate';
import Dictionary from '@/pages/Dictionary';
import ERD from '@/pages/ERD';
import Compliance from '@/pages/Compliance';
import Notifications from '@/pages/Notifications';
import Settings from '@/pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/contracts" element={<Contracts />} />
            <Route path="/contracts/new" element={<ContractCreate />} />
            <Route path="/contracts/:id" element={<ContractDetail />} />
            <Route path="/contracts/:id/edit" element={<ContractCreate />} />
            <Route path="/dictionary" element={<Dictionary />} />
            <Route path="/erd" element={<ERD />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster />
    </QueryClientProvider>
  );
}
```

---

## Docker Configuration

```dockerfile
# frontend/Dockerfile

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# frontend/nginx.conf

server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Handle SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests
    location /api/ {
        proxy_pass http://contract-service:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Add to docker-compose.yml:

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - contract-service
      - dictionary-service
    environment:
      - VITE_API_BASE_URL=http://localhost:8001
```

---

## Iteration Checklist

### Frontend Phase
- [ ] Project scaffold (Vite + React + TypeScript)
- [ ] Tailwind CSS + shadcn/ui setup
- [ ] API client configuration
- [ ] Type definitions
- [ ] React Query hooks
- [ ] Layout components (Sidebar, Header)
- [ ] Dashboard page
- [ ] Contracts list page
- [ ] Contract detail page
- [ ] Contract create/edit form
- [ ] Data dictionary page with search
- [ ] ERD visualization with React Flow
- [ ] Compliance dashboard
- [ ] Notification history page
- [ ] Settings page
- [ ] Docker configuration
- [ ] API proxy setup

---

## Notes for Claude Code

1. **Start with scaffolding** — Use Vite to create the project, then add dependencies
2. **Install shadcn/ui components** — Use `npx shadcn-ui@latest add [component]`
3. **Build pages incrementally** — Start with Dashboard, then Contracts, then others
4. **Type everything** — Use the type definitions provided
5. **Use React Query** — All data fetching should go through the hooks
6. **Keep components small** — Extract reusable pieces into the components folder
7. **Match API endpoints** — The frontend API calls should match what the backend provides

For the ERD page, React Flow requires some setup. Install with:
```bash
npm install reactflow
```

For charts, Recharts is recommended:
```bash
npm install recharts
```
