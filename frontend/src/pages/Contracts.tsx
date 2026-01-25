import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
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
import { useContracts } from '@/hooks/useContracts';
import { useDebounce } from '@/hooks/useDebounce';
import { formatRelativeTime } from '@/lib/utils';

export function Contracts() {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<string>('all');
  const [team, setTeam] = useState<string>('all');

  const debouncedSearch = useDebounce(search, 300);

  const { data, isLoading } = useContracts({
    search: debouncedSearch || undefined,
    status: status !== 'all' ? status : undefined,
    team: team !== 'all' ? team : undefined,
  });

  const contracts = data?.contracts || [];

  // Get unique teams for filter
  const teams = [...new Set(contracts.map((c) => c.publisher_team).filter(Boolean))];

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

      <Card>
        <CardHeader>
          <CardTitle>All Contracts</CardTitle>
          <CardDescription>
            {data?.total || 0} contracts found
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="mb-6 flex flex-wrap gap-4">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search contracts..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={status} onValueChange={setStatus}>
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
            <Select value={team} onValueChange={setTeam}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Team" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Teams</SelectItem>
                {teams.map((t) => (
                  <SelectItem key={t} value={t!}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Table */}
          {isLoading ? (
            <div className="flex items-center justify-center py-10">
              <p className="text-muted-foreground">Loading contracts...</p>
            </div>
          ) : contracts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10">
              <p className="text-muted-foreground">No contracts found</p>
              <Button asChild className="mt-4">
                <Link to="/contracts/new">Create your first contract</Link>
              </Button>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Version</TableHead>
                    <TableHead>Team</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Fields</TableHead>
                    <TableHead>Updated</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {contracts.map((contract) => (
                    <TableRow key={contract.id}>
                      <TableCell>
                        <Link
                          to={`/contracts/${contract.id}`}
                          className="font-medium text-primary hover:underline"
                        >
                          {contract.name}
                        </Link>
                        {contract.description && (
                          <p className="text-sm text-muted-foreground line-clamp-1">
                            {contract.description}
                          </p>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">v{contract.version}</Badge>
                      </TableCell>
                      <TableCell>{contract.publisher_team || '-'}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            contract.status === 'active'
                              ? 'default'
                              : contract.status === 'deprecated'
                              ? 'destructive'
                              : 'secondary'
                          }
                        >
                          {contract.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{contract.fields?.length || 0}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {contract.updated_at
                          ? formatRelativeTime(contract.updated_at)
                          : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
