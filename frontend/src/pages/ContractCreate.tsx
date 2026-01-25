import { useNavigate } from 'react-router-dom';
import { useForm, FormProvider } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  BasicInfoSection,
  PublisherSection,
  SchemaFieldsSection,
  QualityTagsSection,
} from '@/components/contracts';
import { contractFormSchema, type ContractFormData } from '@/lib/validations/contract';
import { useCreateContract } from '@/hooks/useContracts';
import { useToast } from '@/hooks/useToast';

export function ContractCreate() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const createContract = useCreateContract();

  const methods = useForm<ContractFormData>({
    resolver: zodResolver(contractFormSchema),
    defaultValues: {
      name: '',
      version: '1.0.0',
      description: '',
      status: 'draft',
      publisher_team: '',
      publisher_owner: '',
      repository_url: '',
      contact_email: '',
      fields: [],
      quality_metrics: [],
      tags: '',
    },
  });

  const {
    handleSubmit,
    formState: { isSubmitting },
  } = methods;

  const onSubmit = async (data: ContractFormData) => {
    try {
      const contractPayload = {
        name: data.name,
        version: data.version,
        description: data.description || undefined,
        status: data.status,
        publisher: {
          team: data.publisher_team,
          owner: data.publisher_owner,
          repository_url: data.repository_url || undefined,
          contact_email: data.contact_email || undefined,
        },
        schema: data.fields.map((field) => ({
          name: field.name,
          data_type: field.data_type,
          description: field.description || undefined,
          nullable: field.nullable,
          is_pii: field.is_pii,
          is_primary_key: field.is_primary_key,
          is_foreign_key: field.is_foreign_key,
          foreign_key_reference: field.foreign_key_reference || undefined,
          example_value: field.example_value || undefined,
          constraints: [],
        })),
        quality: data.quality_metrics.map((metric) => ({
          metric_type: metric.metric_type,
          threshold: metric.threshold,
          alert_on_breach: metric.alert_on_breach,
        })),
        tags: data.tags
          ? data.tags.split(',').map((tag) => tag.trim()).filter(Boolean)
          : [],
      };

      const result = await createContract.mutateAsync(contractPayload);

      toast({
        title: 'Contract created',
        description: `Successfully created contract "${data.name}"`,
      });

      navigate(`/contracts/${result.id}`);
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to create contract',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/contracts')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Create Contract</h1>
          <p className="text-muted-foreground">Define a new data contract</p>
        </div>
      </div>

      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Card>
            <CardHeader>
              <CardTitle>Contract Details</CardTitle>
              <CardDescription>
                Fill in the details for your new data contract
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="basic" className="space-y-6">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="basic">Basic Info</TabsTrigger>
                  <TabsTrigger value="publisher">Publisher</TabsTrigger>
                  <TabsTrigger value="schema">Schema Fields</TabsTrigger>
                  <TabsTrigger value="quality">Quality & Tags</TabsTrigger>
                </TabsList>

                <TabsContent value="basic">
                  <BasicInfoSection />
                </TabsContent>

                <TabsContent value="publisher">
                  <PublisherSection />
                </TabsContent>

                <TabsContent value="schema">
                  <SchemaFieldsSection />
                </TabsContent>

                <TabsContent value="quality">
                  <QualityTagsSection />
                </TabsContent>
              </Tabs>

              <div className="mt-6 flex justify-end gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/contracts')}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isSubmitting}>
                  <Save className="mr-2 h-4 w-4" />
                  {isSubmitting ? 'Creating...' : 'Create Contract'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </FormProvider>
    </div>
  );
}
