import { z } from 'zod';

export const SuggestedBulletSchema = z.object({
  role_id: z.string().optional(),
  original: z.string(),
  tailored: z.string(),
});

export const GapSchema = z.object({
  skill: z.string().optional(),
  experience: z.string().optional(),
  note: z.string(),
});

export const TailorRequestSchema = z.object({
  job_id: z.string(),
  profile_id: z.string(),
});

export const AutofillAnswersSchema = z.object({
  legalName: z.string().optional(),
  email: z.string().optional(),
  phone: z.string().optional(),
  linkedin: z.string().optional(),
  github: z.string().optional(),
  portfolio: z.string().optional(),
  workAuth: z.string().optional(),
  visaStatus: z.string().optional(),
  salaryExpectation: z.string().optional(),
  availability: z.string().optional(),
  relocation: z.boolean().optional(),
  remote: z.boolean().optional(),
  extra: z.record(z.any()),
});

export const TailorResponseSchema = z.object({
  jd_summary: z.string(),
  skills_required: z.array(z.string()),
  gaps: z.array(GapSchema),
  suggested_bullets: z.array(SuggestedBulletSchema),
  cover_letter_text: z.string(),
  autofill_answers: AutofillAnswersSchema,
  tailored_resume_docx_url: z.string(),
  cover_letter_docx_url: z.string().optional(),
  application_package_docx_url: z.string().optional(),
});

export type SuggestedBullet = z.infer<typeof SuggestedBulletSchema>;
export type Gap = z.infer<typeof GapSchema>;
export type TailorRequest = z.infer<typeof TailorRequestSchema>;
export type AutofillAnswers = z.infer<typeof AutofillAnswersSchema>;
export type TailorResponse = z.infer<typeof TailorResponseSchema>;