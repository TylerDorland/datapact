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
import { Card, CardContent } from '@/components/ui/card';
import { DATA_TYPES } from '@/lib/constants';
import type { ContractFormData } from '@/lib/validations/contract';

export function SchemaFieldsSection() {
  const {
    register,
    control,
    formState: { errors },
    setValue,
    watch,
  } = useFormContext<ContractFormData>();

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'fields',
  });

  const addField = () => {
    append({
      name: '',
      data_type: 'string',
      description: '',
      nullable: true,
      is_pii: false,
      is_primary_key: false,
      is_foreign_key: false,
      foreign_key_reference: '',
      example_value: '',
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Schema Fields</h3>
          <p className="text-sm text-muted-foreground">
            Define the fields in your data contract
          </p>
        </div>
        <Button type="button" onClick={addField} variant="outline" size="sm">
          <Plus className="mr-2 h-4 w-4" />
          Add Field
        </Button>
      </div>

      {errors.fields && !Array.isArray(errors.fields) && (
        <p className="text-sm text-red-600">{errors.fields.message}</p>
      )}

      {fields.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            No fields added yet. Click "Add Field" to get started.
          </CardContent>
        </Card>
      )}

      {fields.map((field, index) => {
        const isForeignKey = watch(`fields.${index}.is_foreign_key`);
        const fieldErrors = errors.fields?.[index];

        return (
          <Card key={field.id}>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Field Name *</Label>
                      <Input
                        placeholder="e.g., order_id"
                        {...register(`fields.${index}.name`)}
                      />
                      {fieldErrors?.name && (
                        <p className="text-sm text-red-600">{fieldErrors.name.message}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label>Data Type *</Label>
                      <Select
                        value={watch(`fields.${index}.data_type`)}
                        onValueChange={(value) =>
                          setValue(`fields.${index}.data_type`, value as typeof DATA_TYPES[number])
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          {DATA_TYPES.map((type) => (
                            <SelectItem key={type} value={type}>
                              {type}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
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

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Input
                      placeholder="Field description"
                      {...register(`fields.${index}.description`)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Example Value</Label>
                    <Input
                      placeholder="e.g., 12345"
                      {...register(`fields.${index}.example_value`)}
                    />
                  </div>
                </div>

                <div className="flex flex-wrap gap-6">
                  <div className="flex items-center gap-2">
                    <Switch
                      id={`fields.${index}.nullable`}
                      checked={watch(`fields.${index}.nullable`)}
                      onCheckedChange={(checked) =>
                        setValue(`fields.${index}.nullable`, checked)
                      }
                    />
                    <Label htmlFor={`fields.${index}.nullable`}>Nullable</Label>
                  </div>

                  <div className="flex items-center gap-2">
                    <Switch
                      id={`fields.${index}.is_pii`}
                      checked={watch(`fields.${index}.is_pii`)}
                      onCheckedChange={(checked) =>
                        setValue(`fields.${index}.is_pii`, checked)
                      }
                    />
                    <Label htmlFor={`fields.${index}.is_pii`}>PII</Label>
                  </div>

                  <div className="flex items-center gap-2">
                    <Switch
                      id={`fields.${index}.is_primary_key`}
                      checked={watch(`fields.${index}.is_primary_key`)}
                      onCheckedChange={(checked) =>
                        setValue(`fields.${index}.is_primary_key`, checked)
                      }
                    />
                    <Label htmlFor={`fields.${index}.is_primary_key`}>Primary Key</Label>
                  </div>

                  <div className="flex items-center gap-2">
                    <Switch
                      id={`fields.${index}.is_foreign_key`}
                      checked={watch(`fields.${index}.is_foreign_key`)}
                      onCheckedChange={(checked) =>
                        setValue(`fields.${index}.is_foreign_key`, checked)
                      }
                    />
                    <Label htmlFor={`fields.${index}.is_foreign_key`}>Foreign Key</Label>
                  </div>
                </div>

                {isForeignKey && (
                  <div className="space-y-2">
                    <Label>Foreign Key Reference</Label>
                    <Input
                      placeholder="e.g., users.id"
                      {...register(`fields.${index}.foreign_key_reference`)}
                    />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
