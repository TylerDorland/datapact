import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Database, ChevronDown, ChevronRight, Users, Tag } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useDictionary } from '@/hooks/useDictionary';
import { useDebounce } from '@/hooks/useDebounce';

export function Dictionary() {
  const [search, setSearch] = useState('');
  const [teamFilter, setTeamFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [expandedDatasets, setExpandedDatasets] = useState<Set<string>>(new Set());

  const debouncedSearch = useDebounce(search, 300);

  const { data: dictionary, isLoading } = useDictionary();

  const datasets = dictionary?.datasets || [];
  const fields = dictionary?.fields || [];
  const teams = dictionary?.teams || [];

  // Filter datasets based on search and filters
  const filteredDatasets = datasets.filter((dataset) => {
    const matchesSearch =
      !debouncedSearch ||
      dataset.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
      dataset.description?.toLowerCase().includes(debouncedSearch.toLowerCase());

    const matchesTeam = teamFilter === 'all' || dataset.publisher_team === teamFilter;
    const matchesStatus = statusFilter === 'all' || dataset.status === statusFilter;

    return matchesSearch && matchesTeam && matchesStatus;
  });

  // Get fields for a specific dataset
  const getDatasetFields = (datasetName: string) => {
    return fields.filter((f) => f.dataset === datasetName);
  };

  const toggleDataset = (datasetName: string) => {
    setExpandedDatasets((prev) => {
      const next = new Set(prev);
      if (next.has(datasetName)) {
        next.delete(datasetName);
      } else {
        next.add(datasetName);
      }
      return next;
    });
  };

  const expandAll = () => {
    setExpandedDatasets(new Set(filteredDatasets.map((d) => d.name)));
  };

  const collapseAll = () => {
    setExpandedDatasets(new Set());
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Data Dictionary</h1>
        <p className="text-muted-foreground">
          Browse and search all datasets and their schemas
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Dataset Catalog</CardTitle>
              <CardDescription>
                {filteredDatasets.length} datasets, {fields.length} total fields
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={expandAll}>
                Expand All
              </Button>
              <Button variant="outline" size="sm" onClick={collapseAll}>
                Collapse All
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="mb-6 flex flex-wrap gap-4">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search datasets..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={teamFilter} onValueChange={setTeamFilter}>
              <SelectTrigger className="w-[150px]">
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
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="deprecated">Deprecated</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Results */}
          {isLoading ? (
            <div className="flex items-center justify-center py-10">
              <p className="text-muted-foreground">Loading datasets...</p>
            </div>
          ) : filteredDatasets.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10">
              <Database className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No datasets found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredDatasets.map((dataset) => {
                const datasetFields = getDatasetFields(dataset.name);
                const isExpanded = expandedDatasets.has(dataset.name);
                const piiCount = datasetFields.filter((f) => f.is_pii).length;

                return (
                  <div key={dataset.name} className="rounded-lg border">
                    <div
                      className="flex items-center justify-between p-4 cursor-pointer hover:bg-muted/50"
                      onClick={() => toggleDataset(dataset.name)}
                    >
                      <div className="flex items-center gap-3">
                        {isExpanded ? (
                          <ChevronDown className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        )}
                        <div>
                          <div className="flex items-center gap-2">
                            <Link
                              to={`/contracts/${dataset.id}`}
                              className="font-semibold hover:underline"
                              onClick={(e) => e.stopPropagation()}
                            >
                              {dataset.name}
                            </Link>
                            <Badge
                              variant={
                                dataset.status === 'active'
                                  ? 'default'
                                  : dataset.status === 'deprecated'
                                  ? 'destructive'
                                  : 'secondary'
                              }
                            >
                              {dataset.status}
                            </Badge>
                            <Badge variant="outline">v{dataset.version}</Badge>
                          </div>
                          {dataset.description && (
                            <p className="text-sm text-muted-foreground mt-1">
                              {dataset.description}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          <span>{dataset.publisher_team}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Tag className="h-4 w-4" />
                          <span>{datasetFields.length} fields</span>
                        </div>
                        {piiCount > 0 && (
                          <Badge variant="destructive">{piiCount} PII</Badge>
                        )}
                      </div>
                    </div>
                    {isExpanded && (
                      <div className="border-t px-4 pb-4">
                        {datasetFields.length === 0 ? (
                          <p className="text-muted-foreground text-sm py-4">
                            No fields defined
                          </p>
                        ) : (
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Field Name</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Nullable</TableHead>
                                <TableHead>PII</TableHead>
                                <TableHead>Primary Key</TableHead>
                                <TableHead>Description</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {datasetFields.map((field) => (
                                <TableRow key={`${field.dataset}-${field.name}`}>
                                  <TableCell className="font-mono">{field.name}</TableCell>
                                  <TableCell>
                                    <Badge variant="outline">{field.data_type}</Badge>
                                  </TableCell>
                                  <TableCell>
                                    {field.nullable ? (
                                      <span className="text-muted-foreground">Yes</span>
                                    ) : (
                                      <Badge variant="default">Required</Badge>
                                    )}
                                  </TableCell>
                                  <TableCell>
                                    {field.is_pii ? (
                                      <Badge variant="destructive">PII</Badge>
                                    ) : (
                                      <span className="text-muted-foreground">No</span>
                                    )}
                                  </TableCell>
                                  <TableCell>
                                    {field.is_primary_key ? (
                                      <Badge variant="secondary">PK</Badge>
                                    ) : (
                                      <span className="text-muted-foreground">-</span>
                                    )}
                                  </TableCell>
                                  <TableCell className="text-muted-foreground max-w-[300px] truncate">
                                    {field.description || '-'}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
