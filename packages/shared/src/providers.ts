import { Provider } from './schemas/jobPosting';

export interface ProviderPattern {
  provider: Provider;
  patterns: Array<RegExp | ((url: URL) => boolean)>;
}

export const PROVIDER_PATTERNS: ProviderPattern[] = [
  {
    provider: 'GREENHOUSE',
    patterns: [
      /^job-boards\.greenhouse\.io\/[^/]+\/jobs\/\d+/i,
      /^boards\.greenhouse\.io\/[^/]+\/jobs\/\d+/i,
      /^.*greenhouse\.io.*jobs.*/i,
    ],
  },
  {
    provider: 'LEVER',
    patterns: [
      /^jobs\.lever\.co\/[^/]+\/[^/]+/i,
      /^.*lever\.co.*/i,
    ],
  },
  {
    provider: 'ASHBY',
    patterns: [
      /^jobs\.ashbyhq\.com\/[^/]+\/[^/]+/i,
      /^.*ashbyhq\.com.*/i,
    ],
  },
  {
    provider: 'SMARTRECRUITERS',
    patterns: [
      /^jobs\.smartrecruiters\.com\/[^/]+\/[^/]+/i,
      /^.*smartrecruiters\.com.*/i,
    ],
  },
  {
    provider: 'WORKDAY',
    patterns: [
      /^.*\.wd\d+\.myworkdayjobs\.com\/.+/i,
      /^.*myworkdayjobs\.com.*/i,
    ],
  },
  {
    provider: 'ORACLE_CX',
    patterns: [
      /^.*\.fa.*\.oraclecloud\.com\/hcmUI\/CandidateExperience.*/i,
      /^.*oraclecloud\.com.*CandidateExperience.*/i,
    ],
  },
  {
    provider: 'AVATURE',
    patterns: [
      /^.*\.avature\.net\/.+/i,
      /^.*avature\.net.*/i,
    ],
  },
  {
    provider: 'SUCCESSFACTORS',
    patterns: [
      /^.*\.successfactors\.com.*/i,
      /^.*successfactors\.com.*/i,
    ],
  },
  {
    provider: 'TALEO',
    patterns: [
      /^.*\.taleo\.net.*/i,
      /^.*taleo\.net.*/i,
    ],
  },
  {
    provider: 'ICIMS',
    patterns: [
      /^.*\.icims\.com.*/i,
      /^.*icims\.com.*/i,
    ],
  },
  {
    provider: 'PHENOM',
    patterns: [
      /^.*\.phenompeople\.com.*/i,
      /^.*phenompeople\.com.*/i,
    ],
  },
];

export function detectProvider(urlString: string): Provider {
  try {
    const url = new URL(urlString);
    const hostname = url.hostname;
    const pathname = url.pathname;
    const fullPath = hostname + pathname;

    for (const { provider, patterns } of PROVIDER_PATTERNS) {
      for (const pattern of patterns) {
        if (typeof pattern === 'function') {
          if (pattern(url)) {
            return provider;
          }
        } else if (pattern.test(fullPath)) {
          return provider;
        }
      }
    }

    return 'UNKNOWN';
  } catch (error) {
    return 'UNKNOWN';
  }
}

export function extractGreenhouseIds(urlString: string): { board: string; jobId: string } | null {
  const match = urlString.match(/job-boards\.greenhouse\.io\/([^/]+)\/jobs\/(\d+)/i) ||
                urlString.match(/boards\.greenhouse\.io\/([^/]+)\/jobs\/(\d+)/i);
  if (match) {
    return { board: match[1], jobId: match[2] };
  }
  return null;
}

export function extractLeverIds(urlString: string): { account: string; postingId: string } | null {
  const match = urlString.match(/jobs\.lever\.co\/([^/]+)\/([^/]+)/i);
  if (match) {
    return { account: match[1], postingId: match[2] };
  }
  return null;
}

export function extractAshbyIds(urlString: string): { company: string; jobId: string } | null {
  const match = urlString.match(/jobs\.ashbyhq\.com\/([^/]+)\/([^/]+)/i);
  if (match) {
    return { company: match[1], jobId: match[2] };
  }
  return null;
}

export function extractSmartRecruitersIds(urlString: string): { companyIdentifier: string; postingId: string } | null {
  const match = urlString.match(/jobs\.smartrecruiters\.com\/([^/]+)\/([^/]+)/i);
  if (match) {
    return { companyIdentifier: match[1], postingId: match[2] };
  }
  return null;
}
