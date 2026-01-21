import { z } from 'zod';

export const ValidationSchema = z.object({
  pattern: z.string().optional(),
  min: z.number().optional(),
  max: z.number().optional(),
});

export const SelectOptionSchema = z.object({
  value: z.string(),
  label: z.string(),
});

export const ApplicationFieldTypeSchema = z.enum([
  'text',
  'textarea',
  'email',
  'tel',
  'url',
  'select',
  'radio',
  'checkbox',
  'date',
  'file',
  'unknown',
]);

export const ApplicationFieldSchema = z.object({
  key: z.string(),
  label: z.string(),
  type: ApplicationFieldTypeSchema,
  required: z.boolean(),
  options: z.array(SelectOptionSchema).optional(),
  validation: ValidationSchema.optional(),
  source_hint: z.string().optional(),
});

export type Validation = z.infer<typeof ValidationSchema>;
export type SelectOption = z.infer<typeof SelectOptionSchema>;
export type ApplicationFieldType = z.infer<typeof ApplicationFieldTypeSchema>;
export type ApplicationField = z.infer<typeof ApplicationFieldSchema>;
