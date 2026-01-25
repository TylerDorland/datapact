import { useEffect, useMemo, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useERD } from '@/hooks/useDictionary';
import type { ERDNodeField } from '@/types/dictionary';

// Custom node component for datasets
function DatasetNode({
  data,
}: {
  data: { label: string; fields: ERDNodeField[]; status?: string };
}) {
  return (
    <div className="rounded-lg border bg-card shadow-md min-w-[220px]">
      <div className="border-b bg-primary/10 px-4 py-2 rounded-t-lg flex items-center justify-between">
        <p className="font-semibold text-sm">{data.label}</p>
        {data.status && (
          <Badge
            variant={
              data.status === 'active'
                ? 'default'
                : data.status === 'deprecated'
                ? 'destructive'
                : 'secondary'
            }
            className="text-[10px] h-5"
          >
            {data.status}
          </Badge>
        )}
      </div>
      <div className="p-2 max-h-[200px] overflow-auto">
        {data.fields?.slice(0, 10).map((field) => (
          <div
            key={field.name}
            className="text-xs py-1 px-2 font-mono text-muted-foreground flex items-center gap-2"
          >
            <span className="flex-1">{field.name}</span>
            <span className="text-[10px] opacity-60">{field.data_type}</span>
            {field.is_primary_key && (
              <span className="text-[10px] font-bold text-primary">PK</span>
            )}
            {field.is_foreign_key && (
              <span className="text-[10px] font-bold text-blue-500">FK</span>
            )}
            {field.is_pii && (
              <span className="text-[10px] font-bold text-red-500">PII</span>
            )}
          </div>
        ))}
        {data.fields?.length > 10 && (
          <div className="text-xs py-1 px-2 text-muted-foreground italic">
            +{data.fields.length - 10} more fields
          </div>
        )}
        {(!data.fields || data.fields.length === 0) && (
          <div className="text-xs py-1 px-2 text-muted-foreground italic">No fields</div>
        )}
      </div>
    </div>
  );
}

const nodeTypes = {
  dataset: DatasetNode,
};

export function ERD() {
  const [team, setTeam] = useState<string>('all');
  const { data: erdData, isLoading } = useERD(team !== 'all' ? team : undefined);

  // Transform ERD data to React Flow format
  const { flowNodes, flowEdges } = useMemo(() => {
    if (!erdData?.nodes) {
      return { flowNodes: [], flowEdges: [] };
    }

    const nodes: Node[] = erdData.nodes.map((node, index) => ({
      id: node.id,
      type: 'dataset',
      position: {
        x: (index % 3) * 320 + 50,
        y: Math.floor(index / 3) * 300 + 50,
      },
      data: {
        label: node.label || node.id,
        fields: node.fields || [],
        status: node.status,
      },
    }));

    const edges: Edge[] = erdData.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      type: 'smoothstep',
      markerEnd: { type: MarkerType.ArrowClosed },
      style: {
        stroke:
          edge.type === 'subscription'
            ? 'hsl(var(--primary))'
            : 'hsl(var(--muted-foreground))',
        strokeDasharray: edge.type === 'subscription' ? '5 5' : undefined,
      },
    }));

    return { flowNodes: nodes, flowEdges: edges };
  }, [erdData]);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Sync React Flow state when data changes
  useEffect(() => {
    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [flowNodes, flowEdges, setNodes, setEdges]);

  // Get unique teams for filter
  const teams = useMemo(() => {
    if (!erdData?.nodes) return [];
    return [
      ...new Set(erdData.nodes.map((n) => n.publisher_team).filter(Boolean)),
    ] as string[];
  }, [erdData]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Entity Relationship Diagram</h1>
        <p className="text-muted-foreground">
          Visualize relationships between your data contracts
        </p>
      </div>

      <Card className="h-[calc(100vh-250px)]">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Data Relationships</CardTitle>
              <CardDescription>
                {nodes.length} datasets, {edges.length} relationships
              </CardDescription>
            </div>
            <Select value={team} onValueChange={setTeam}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by team" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Teams</SelectItem>
                {teams.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent className="h-[calc(100%-80px)] p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-muted-foreground">Loading diagram...</p>
            </div>
          ) : nodes.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-muted-foreground">No data to display</p>
            </div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              nodeTypes={nodeTypes}
              fitView
              attributionPosition="bottom-right"
            >
              <Background />
              <Controls />
              <MiniMap
                nodeColor="hsl(var(--primary))"
                maskColor="hsl(var(--background) / 0.8)"
              />
              <Panel position="top-left" className="bg-card p-2 rounded shadow text-xs">
                Drag to pan, scroll to zoom
              </Panel>
            </ReactFlow>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
