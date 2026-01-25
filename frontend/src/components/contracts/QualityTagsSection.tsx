import { useFormContext, useFieldArray } from 'react-hook-form';
import { Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { METRIC_TYPES } from '@/lib/constants';
import type { ContractFormData } from '@/lib/validations/contract';

export function QualityTagsSection() {
  const {
    register,
    control,
    formState: { errors },
    setValue,
    watch,
  } = useFormContext<ContractFormData>();

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'quality_metrics',
  });

  const addMetric = () => {
    append({
      metric_type: 'completeness',
      threshold: '',
      alert_on_breach: true,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Quality Metrics</CardTitle>
              <Button type="button" onClick={addMetric} variant="outline" size="sm">
                <Plus className="mr-2 h-4 w-4" />
                Add Metric
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {fields.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">
                No quality metrics defined. Add metrics to monitor data quality.
              </p>
            ) : (
              <div className="space-y-4">
                {fields.map((field, index) => {
                  const metricErrors = errors.quality_metrics?.[index];

                  return (
                    <div
                      key={field.id}
                      className="flex items-start gap-4 p-4 border rounded-lg"
                    >
                      <div className="flex-1 grid grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label>Metric Type</Label>
                          <Select
                            value={watch(`quality_metrics.${index}.metric_type`)}
                            onValueChange={(value) =>
                              setValue(
                                `quality_metrics.${index}.metric_type`,
                                value as typeof METRIC_TYPES[number]
                              )
                            }
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                            <SelectContent>
                              {METRIC_TYPES.map((type) => (
                                <SelectItem key={type} value={type}>
                                  {type.charAt(0).toUpperCase() + type.slice(1)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-2">
                          <Label>Threshold *</Label>
                          <Input
                            placeholder="e.g., 99%"
                            {...register(`quality_metrics.${index}.threshold`)}
                          />
                          {metricErrors?.threshold && (
                            <p className="text-sm text-red-600">
                              {metricErrors.threshold.message}
                            </p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <Label>Alert on Breach</Label>
                          <div className="pt-2">
                            <Switch
                              checked={watch(`quality_metrics.${index}.alert_on_breach`)}
                              onCheckedChange={(checked) =>
                                setValue(`quality_metrics.${index}.alert_on_breach`, checked)
                              }
                            />
                          </div>
                        </div>
                      </div>

                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => remove(index)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div>
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Tags</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Label htmlFor="tags">Tags (comma-separated)</Label>
              <Input
                id="tags"
                placeholder="e.g., orders, commerce, production"
                {...register('tags')}
              />
              <p className="text-sm text-muted-foreground">
                Add tags to help categorize and search for this contract
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
