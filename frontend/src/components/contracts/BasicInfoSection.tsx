import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CONTRACT_STATUSES } from '@/lib/constants';
import type { ContractFormData } from '@/lib/validations/contract';

export function BasicInfoSection() {
  const {
    register,
    formState: { errors },
    setValue,
    watch,
  } = useFormContext<ContractFormData>();

  const status = watch('status');

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Contract Name *</Label>
        <Input
          id="name"
          placeholder="e.g., user_orders"
          {...register('name')}
        />
        {errors.name && (
          <p className="text-sm text-red-600">{errors.name.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="version">Version *</Label>
        <Input
          id="version"
          placeholder="e.g., 1.0.0"
          {...register('version')}
        />
        {errors.version && (
          <p className="text-sm text-red-600">{errors.version.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          placeholder="Describe the purpose and contents of this contract..."
          {...register('description')}
        />
        {errors.description && (
          <p className="text-sm text-red-600">{errors.description.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="status">Status</Label>
        <Select
          value={status}
          onValueChange={(value) => setValue('status', value as typeof status)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select status" />
          </SelectTrigger>
          <SelectContent>
            {CONTRACT_STATUSES.map((s) => (
              <SelectItem key={s} value={s}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.status && (
          <p className="text-sm text-red-600">{errors.status.message}</p>
        )}
      </div>
    </div>
  );
}
