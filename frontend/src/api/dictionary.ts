import { dictionaryClient } from './client';
import type { Dictionary, DictionaryField, ERDData } from '@/types/dictionary';

export interface SearchParams {
  q: string;
  scope?: 'all' | 'fields' | 'datasets';
  data_type?: string;
  is_pii?: boolean;
  team?: string;
  limit?: number;
}

export interface SearchResponse {
  results: {
    fields: DictionaryField[];
    datasets: Array<{
      name: string;
      description?: string;
      publisher: string;
      relevance: number;
    }>;
  };
  total: number;
  query: string;
}

export const dictionaryApi = {
  getFull: async (): Promise<Dictionary> => {
    const { data } = await dictionaryClient.get('/api/v1/dictionary');
    return data;
  },

  search: async (params: SearchParams): Promise<SearchResponse> => {
    const { data } = await dictionaryClient.get('/api/v1/search', { params });
    return data;
  },

  suggest: async (prefix: string, limit?: number): Promise<{ suggestions: string[] }> => {
    const { data } = await dictionaryClient.get('/api/v1/search/suggest', {
      params: { prefix, limit },
    });
    return data;
  },

  getFieldLineage: async (
    dataset: string,
    field: string
  ): Promise<{
    upstream: Array<{ dataset: string; field: string }>;
    downstream: Array<{ dataset: string; field: string }>;
  }> => {
    const { data } = await dictionaryClient.get(
      `/api/v1/dictionary/datasets/${dataset}/fields/${field}/lineage`
    );
    return data;
  },

  getERD: async (params?: { team?: string }): Promise<ERDData> => {
    const { data } = await dictionaryClient.get('/api/v1/erd/json', { params });
    return data;
  },

  getERDMermaid: async (team?: string): Promise<string> => {
    const { data } = await dictionaryClient.get('/api/v1/erd/mermaid', {
      params: { team },
    });
    return data;
  },
};
