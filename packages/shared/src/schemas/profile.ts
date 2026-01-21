import { z } from 'zod';

export const LinkSchema = z.object({
  type: z.string(),
  url: z.string().url().optional(),
  label: z.string().optional(),
});

export const WorkExperienceSchema = z.object({
  company: z.string(),
  title: z.string(),
  startDate: z.string(), // ISO date string or "YYYY-MM"
  endDate: z.string().optional(), // ISO date string, "YYYY-MM", or "Present"
  location: z.string().optional(),
  employmentType: z.string().optional(),
  description: z.string().optional(),
  technologies: z.array(z.string()),
  achievements: z.array(z.string()),
  bullets: z.array(z.string()),
});

export const EducationSchema = z.object({
  school: z.string(),
  degree: z.string(),
  field: z.string().optional(),
  startDate: z.string().optional(),
  endDate: z.string().optional(),
  gpa: z.number().optional(),
  grade: z.string().optional(),
  honors: z.array(z.string()).optional(),
  relevantCoursework: z.array(z.string()).optional(),
  activities: z.array(z.string()).optional(),
  thesis: z.string().optional(),
  bullets: z.array(z.string()).optional(),
});

export const ProjectSchema = z.object({
  name: z.string(),
  link: z.string().url().optional(),
  description: z.string(),
  startDate: z.string().optional(),
  endDate: z.string().optional(),
  role: z.string().optional(),
  teamSize: z.number().optional(),
  status: z.string().optional(),
  outcomes: z.array(z.string()).optional(),
  tech: z.array(z.string()),
  bullets: z.array(z.string()),
});

export const SkillSchema = z.object({
  name: z.string(),
  category: z.string().optional(),
  level: z.enum(['beginner', 'intermediate', 'advanced', 'expert']).optional(),
  yearsExperience: z.number().optional(),
});

export const CertificationSchema = z.object({
  name: z.string(),
  issuer: z.string().optional(),
  date: z.string().optional(),
  expiryDate: z.string().optional(),
  credentialId: z.string().optional(),
  url: z.string().url().optional(),
  description: z.string().optional(),
  skills: z.array(z.string()).optional(),
  verification: z.string().optional(),
});

export const AwardSchema = z.object({
  name: z.string(),
  issuer: z.string().optional(),
  date: z.string().optional(),
  category: z.string().optional(),
  description: z.string().optional(),
  recognition: z.string().optional(),
});

export const LanguageSchema = z.object({
  name: z.string(),
  proficiency: z.enum(['native', 'fluent', 'conversational', 'basic']).optional(),
});

export const PreferencesSchema = z.object({
  visaStatus: z.string().optional(),
  workAuth: z.string().optional(),
  relocation: z.boolean().optional(),
  remote: z.boolean().optional(),
  salary: z.string().optional(),
  availability: z.string().optional(),
});

export const BasicsSchema = z.object({
  firstName: z.string(),
  lastName: z.string(),
  email: z.string().email().optional(),
  phone: z.string().optional(),
  location: z.string().optional(),
  headline: z.string().optional(),
  links: z.array(LinkSchema),
});

export const ProfileSchema = z.object({
  basics: BasicsSchema,
  work_experience: z.array(WorkExperienceSchema),
  education: z.array(EducationSchema),
  projects: z.array(ProjectSchema),
  skills: z.array(SkillSchema),
  certifications: z.array(CertificationSchema).optional(),
  awards: z.array(AwardSchema).optional(),
  preferences: PreferencesSchema.optional(),
});

export type Link = z.infer<typeof LinkSchema>;
export type WorkExperience = z.infer<typeof WorkExperienceSchema>;
export type Education = z.infer<typeof EducationSchema>;
export type Project = z.infer<typeof ProjectSchema>;
export type Skill = z.infer<typeof SkillSchema>;
export type Language = z.infer<typeof LanguageSchema>;
export type Certification = z.infer<typeof CertificationSchema>;
export type Award = z.infer<typeof AwardSchema>;
export type Preferences = z.infer<typeof PreferencesSchema>;
export type Basics = z.infer<typeof BasicsSchema>;
export type Profile = z.infer<typeof ProfileSchema>;
