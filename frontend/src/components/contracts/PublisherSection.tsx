import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { ContractFormData } from '@/lib/validations/contract';

export function PublisherSection() {
  const {
    register,
    formState: { errors },
  } = useFormContext<ContractFormData>();

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="publisher_team">Team *</Label>
        <Input
          id="publisher_team"
          placeholder="e.g., commerce"
          {...register('publisher_team')}
        />
        {errors.publisher_team && (
          <p className="text-sm text-red-600">{errors.publisher_team.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="publisher_owner">Owner *</Label>
        <Input
          id="publisher_owner"
          placeholder="e.g., orders-service"
          {...register('publisher_owner')}
        />
        {errors.publisher_owner && (
          <p className="text-sm text-red-600">{errors.publisher_owner.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="repository_url">Repository URL</Label>
        <Input
          id="repository_url"
          placeholder="e.g., https://github.com/org/repo"
          {...register('repository_url')}
        />
        {errors.repository_url && (
          <p className="text-sm text-red-600">{errors.repository_url.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="contact_email">Contact Email</Label>
        <Input
          id="contact_email"
          type="email"
          placeholder="e.g., team@company.com"
          {...register('contact_email')}
        />
        {errors.contact_email && (
          <p className="text-sm text-red-600">{errors.contact_email.message}</p>
        )}
      </div>
    </div>
  );
}
