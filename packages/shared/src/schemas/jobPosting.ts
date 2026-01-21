import { z } from 'zod';
import { ApplicationFieldSchema } from './application';

export const ProviderSchema = z.enum([
  'GREENHOUSE',
  'LEVER',
  'ASHBY',
  'SMARTRECRUITERS',
  'WORKDAY',
  'ORACLE_CX',
  'AVATURE',
  'SUCCESSFACTORS',
  'TALEO',
  'ICIMS',
  'PHENOM',
  'UNKNOWN',
]);

export const EmploymentTypeSchema = z.enum([
  'FULL_TIME',
  'PART_TIME',
  'CONTRACT',
  'TEMPORARY',
  'INTERNSHIP',
  'FREELANCE',
  'OTHER',
]);

export const RawExtractionSchema = z.object({
  provider_payload: z.record(z.any()).optional(),
  extraction_path: z.string(),
  fetched_at: z.string(), // ISO datetime
  warnings: z.array(z.string()),
});

export const JobPostingNormalizedSchema = z.object({
  source_url: z.string().url(),
  provider: ProviderSchema,
  company_name: z.string().optional(),
  title: z.string().optional(),
  location: z.string().optional(),
  employment_type: EmploymentTypeSchema.optional(),
  apply_url: z.string().url().optional(),
  description_html: z.string().optional(),
  description_text: z.string(), // Required if extraction succeeded
  application_form_schema: z.array(ApplicationFieldSchema).optional(),
  raw: RawExtractionSchema,
});

export type Provider = z.infer<typeof ProviderSchema>;
export type EmploymentType = z.infer<typeof EmploymentTypeSchema>;
export type RawExtraction = z.infer<typeof RawExtractionSchema>;
export type JobPostingNormalized = z.infer<typeof JobPostingNormalizedSchema>;
