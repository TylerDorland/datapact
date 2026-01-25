import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Clock, Users, Shield, AlertTriangle, UserPlus } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useContract, useContractVersions, useSubscribeToContract } from '@/hooks/useContracts';
import { useContractCompliance, useTriggerComplianceCheck } from '@/hooks/useCompliance';
import { formatRelativeTime, formatDate } from '@/lib/utils';
import { useToast } from '@/hooks/useToast';

export function ContractDetail() {
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();
  const [subscribeOpen, setSubscribeOpen] = useState(false);
  const [subscribeForm, setSubscribeForm] = useState({
    team: '',
    use_case: '',
    contact_email: '',
  });

  const { data: contract, isLoading } = useContract(id!);
  const { data: versions } = useContractVersions(id!);
  const { data: compliance } = useContractCompliance(id!);
  const triggerCheck = useTriggerComplianceCheck();
  const subscribe = useSubscribeToContract();

  const handleTriggerCheck = async () => {
    try {
      await triggerCheck.mutateAsync({ contractId: id! });
      toast({
        title: 'Compliance check triggered',
        description: 'The check will run shortly.',
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to trigger compliance check.',
        variant: 'destructive',
      });
    }
  };

  const handleSubscribe = async () => {
    if (!subscribeForm.team.trim()) {
      toast({
        title: 'Error',
        description: 'Team name is required.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await subscribe.mutateAsync({
        contractId: id!,
        subscription: {
          team: subscribeForm.team,
          use_case: subscribeForm.use_case || undefined,
          contact_email: subscribeForm.contact_email || undefined,
        },
      });
      toast({
        title: 'Subscribed successfully',
        description: `Your team "${subscribeForm.team}" is now subscribed to this contract.`,
      });
      setSubscribeOpen(false);
      setSubscribeForm({ team: '', use_case: '', contact_email: '' });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to subscribe to contract.',
        variant: 'destructive',
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-muted-foreground">Loading contract...</p>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-muted-foreground">Contract not found</p>
        <Button asChild className="mt-4">
          <Link to="/contracts">Back to Contracts</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/contracts">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <Badge variant={contract.status === 'active' ? 'default' : 'secondary'}>
              {contract.status}
            </Badge>
            <Badge variant="outline">v{contract.version}</Badge>
          </div>
          <h1 className="text-3xl font-bold">{contract.name}</h1>
          {contract.description && (
            <p className="text-muted-foreground mt-1">{contract.description}</p>
          )}
        </div>
        <div className="flex gap-2">
          <Dialog open={subscribeOpen} onOpenChange={setSubscribeOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <UserPlus className="mr-2 h-4 w-4" />
                Subscribe
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Subscribe to Contract</DialogTitle>
                <DialogDescription>
                  Register your team as a consumer of the "{contract.name}" contract.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="team">Team Name *</Label>
                  <Input
                    id="team"
                    placeholder="e.g., analytics-team"
                    value={subscribeForm.team}
                    onChange={(e) =>
                      setSubscribeForm((prev) => ({ ...prev, team: e.target.value }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="use_case">Use Case</Label>
                  <Textarea
                    id="use_case"
                    placeholder="Describe how your team will use this data..."
                    value={subscribeForm.use_case}
                    onChange={(e) =>
                      setSubscribeForm((prev) => ({ ...prev, use_case: e.target.value }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="contact_email">Contact Email</Label>
                  <Input
                    id="contact_email"
                    type="email"
                    placeholder="team@company.com"
                    value={subscribeForm.contact_email}
                    onChange={(e) =>
                      setSubscribeForm((prev) => ({ ...prev, contact_email: e.target.value }))
                    }
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setSubscribeOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSubscribe} disabled={subscribe.isPending}>
                  {subscribe.isPending ? 'Subscribing...' : 'Subscribe'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Button variant="outline" onClick={handleTriggerCheck} disabled={triggerCheck.isPending}>
            <Shield className="mr-2 h-4 w-4" />
            Run Check
          </Button>
        </div>
      </div>

      {/* Meta Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Publisher</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-lg font-semibold">{contract.publisher_team || '-'}</p>
            <p className="text-sm text-muted-foreground">{contract.publisher_owner || '-'}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Updated</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-lg font-semibold">
              {contract.updated_at ? formatRelativeTime(contract.updated_at) : '-'}
            </p>
            <p className="text-sm text-muted-foreground">
              {contract.updated_at ? formatDate(contract.updated_at) : '-'}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance</CardTitle>
            {compliance?.status === 'passed' ? (
              <Shield className="h-4 w-4 text-green-500" />
            ) : compliance?.status === 'failed' ? (
              <AlertTriangle className="h-4 w-4 text-red-500" />
            ) : (
              <Shield className="h-4 w-4 text-muted-foreground" />
            )}
          </CardHeader>
          <CardContent>
            <p className="text-lg font-semibold capitalize">
              {compliance?.status || 'Not checked'}
            </p>
            <p className="text-sm text-muted-foreground">
              {compliance?.last_check
                ? formatRelativeTime(compliance.last_check)
                : 'No checks yet'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="schema">
        <TabsList>
          <TabsTrigger value="schema">Schema ({contract.fields?.length || 0})</TabsTrigger>
          <TabsTrigger value="quality">Quality Metrics</TabsTrigger>
          <TabsTrigger value="subscribers">Subscribers ({contract.subscribers?.length || 0})</TabsTrigger>
          <TabsTrigger value="versions">Versions ({versions?.length || 0})</TabsTrigger>
        </TabsList>

        <TabsContent value="schema" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Schema Fields</CardTitle>
              <CardDescription>Fields defined in this contract</CardDescription>
            </CardHeader>
            <CardContent>
              {contract.fields?.length ? (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Nullable</TableHead>
                        <TableHead>PII</TableHead>
                        <TableHead>Description</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {contract.fields.map((field) => (
                        <TableRow key={field.id}>
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
                          <TableCell className="text-muted-foreground">
                            {field.description || '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-muted-foreground">No fields defined</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="quality" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Quality Metrics</CardTitle>
              <CardDescription>SLA and quality requirements</CardDescription>
            </CardHeader>
            <CardContent>
              {contract.quality_metrics?.length ? (
                <div className="space-y-4">
                  {contract.quality_metrics.map((metric, index) => (
                    <div key={index} className="rounded-lg border p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium capitalize">{metric.metric_type}</p>
                          {metric.field_name && (
                            <p className="text-sm text-muted-foreground">
                              Field: {metric.field_name}
                            </p>
                          )}
                        </div>
                        <Badge variant="outline">
                          Threshold: {metric.threshold}
                          {metric.metric_type === 'freshness' ? 'h' : '%'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No quality metrics defined</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="subscribers" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Subscribers</CardTitle>
              <CardDescription>Teams using this contract</CardDescription>
            </CardHeader>
            <CardContent>
              {contract.subscribers?.length ? (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Team</TableHead>
                        <TableHead>Use Case</TableHead>
                        <TableHead>Contact</TableHead>
                        <TableHead>Subscribed</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {contract.subscribers.map((sub) => (
                        <TableRow key={sub.id}>
                          <TableCell className="font-medium">{sub.team}</TableCell>
                          <TableCell>{sub.use_case || '-'}</TableCell>
                          <TableCell>{sub.contact_email || '-'}</TableCell>
                          <TableCell className="text-muted-foreground">
                            {sub.subscribed_at
                              ? formatRelativeTime(sub.subscribed_at)
                              : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-muted-foreground">No subscribers yet</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="versions" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Version History</CardTitle>
              <CardDescription>Previous versions of this contract</CardDescription>
            </CardHeader>
            <CardContent>
              {versions?.length ? (
                <div className="space-y-4">
                  {versions.map((version) => (
                    <div
                      key={version.id}
                      className="flex items-center justify-between rounded-lg border p-4"
                    >
                      <div>
                        <p className="font-medium">v{version.version}</p>
                        <p className="text-sm text-muted-foreground">
                          {version.created_at
                            ? formatDate(version.created_at)
                            : '-'}
                        </p>
                      </div>
                      {version.change_description && (
                        <p className="text-sm text-muted-foreground">
                          {version.change_description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No version history</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
