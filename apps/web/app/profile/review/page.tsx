'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../lib/useAuth';
import { apiClient } from '../../../lib/api';

interface ProfileData {
  basics: {
    firstName: string;
    lastName: string;
    email: string | null;
    phone: string | null;
    location: string | null;
    headline: string | null;
    summary: string | null;
    languages: string[] | null;
    links: Array<{
      type: string;
      url: string;
      label: string;
    }>;
  };
  work_experience: Array<{
    company: string;
    title: string;
    startDate: string;
    endDate: string | null;
    location: string | null;
    employmentType: string | null;
    description: string | null;
    technologies: string[];
    achievements: string[];
    bullets: string[];
  }>;
  education: Array<{
    school: string;
    degree: string;
    field: string | null;
    startDate: string | null;
    endDate: string | null;
    gpa: number | null;
    grade: string | null;
    honors: string[] | null;
    relevantCoursework: string[] | null;
    activities: string[] | null;
    thesis: string | null;
    bullets: string[] | null;
  }>;
  projects: Array<{
    name: string;
    link: string | null;
    description: string;
    startDate: string | null;
    endDate: string | null;
    role: string | null;
    teamSize: number | null;
    status: string | null;
    outcomes: string[] | null;
    tech: string[];
    bullets: string[];
  }>;
  skills: Array<{
    name: string;
    category: string | null;
    level: string | null;
    yearsExperience: number | null;
  }>;
  languages?: Array<{
    name: string;
    proficiency: string | null;
  }>;
  certifications?: Array<{
    name: string;
    issuer: string | null;
    date: string | null;
    expiryDate: string | null;
    credentialId: string | null;
    url: string | null;
    description: string | null;
    skills: string[] | null;
    verification: string | null;
  }>;
  awards?: Array<{
    name: string;
    issuer: string | null;
    date: string | null;
    category: string | null;
    description: string | null;
    recognition: string | null;
  }>;
  preferences?: {
    visaStatus: string | null;
    workAuth: string | null;
    relocation: boolean | null;
    remote: boolean | null;
    salary: string | null;
    availability: string | null;
  };
}

export default function ProfileReviewPage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState<'form' | 'markdown'>('form');
  const [markdownContent, setMarkdownContent] = useState('');
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    fetchProfile();
  }, [isAuthenticated, router]);

  const fetchProfile = async () => {
    try {
      const response = await apiClient.get('/v1/profile/me');
      if (response.profile) {
        setProfile(response.profile);
      }
    } catch (err) {
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const saveProfile = async () => {
    if (!profile) return;

    setSaving(true);
    try {
      await apiClient.put('/v1/profile/me', { profile });
      router.push('/dashboard');
    } catch (err) {
      setError('Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const addWorkExperience = () => {
    if (!profile) return;

    const newExp = {
      company: '',
      title: '',
      startDate: '',
      endDate: null,
      location: null,
      employmentType: null,
      description: null,
      technologies: [],
      achievements: [],
      bullets: ['']
    };

    setProfile({
      ...profile,
      work_experience: [...profile.work_experience, newExp]
    });
  };

  const addEducation = () => {
    if (!profile) return;

    const newEdu = {
      school: '',
      degree: '',
      field: null,
      startDate: null,
      endDate: null,
      gpa: null,
      grade: null,
      honors: null,
      relevantCoursework: null,
      activities: null,
      thesis: null,
      bullets: null
    };

    setProfile({
      ...profile,
      education: [...profile.education, newEdu]
    });
  };

  const addProject = () => {
    if (!profile) return;

    const newProj = {
      name: '',
      link: null,
      description: '',
      startDate: null,
      endDate: null,
      role: null,
      teamSize: null,
      status: null,
      outcomes: null,
      tech: [],
      bullets: []
    };

    setProfile({
      ...profile,
      projects: [...profile.projects, newProj]
    });
  };

  const addSkill = () => {
    if (!profile) return;

    const newSkill = {
      name: '',
      category: null,
      level: null,
      yearsExperience: null
    };

    setProfile({
      ...profile,
      skills: [...profile.skills, newSkill]
    });
  };

  const addLanguage = () => {
    if (!profile) return;

    const newLanguage = {
      name: '',
      proficiency: null
    };

    const currentLanguages = profile.languages || [];
    setProfile({
      ...profile,
      languages: [...currentLanguages, newLanguage]
    });
  };

  const generateMarkdown = (profileData: ProfileData): string => {
    let markdown = '';

    // Header with name
    markdown += `# ${profileData.basics.firstName} ${profileData.basics.lastName}\n\n`;

    // Contact Information
    const contactInfo = [];
    if (profileData.basics.email) contactInfo.push(`📧 ${profileData.basics.email}`);
    if (profileData.basics.phone) contactInfo.push(`📱 ${profileData.basics.phone}`);
    if (profileData.basics.location) contactInfo.push(`📍 ${profileData.basics.location}`);

    if (contactInfo.length > 0) {
      markdown += '## Contact Information\n\n';
      contactInfo.forEach(info => markdown += `${info}\n`);
      markdown += '\n';
    }

    // Professional Summary
    if (profileData.basics.summary) {
      markdown += `## Professional Summary\n\n${profileData.basics.summary}\n\n`;
    }

    // Languages
    if (profileData.basics.languages && profileData.basics.languages.length > 0) {
      markdown += '## Languages\n\n';
      markdown += `- ${profileData.basics.languages.join(', ')}\n\n`;
    }

    // Work Experience
    if (profileData.work_experience.length > 0) {
      markdown += '## Work Experience\n\n';
      profileData.work_experience.forEach(exp => {
        markdown += `### ${exp.title}\n`;
        markdown += `**${exp.company}**`;
        if (exp.location) markdown += ` • ${exp.location}`;
        markdown += '\n';

        const startDate = exp.startDate || '';
        const endDate = exp.endDate || 'Present';
        markdown += `**${startDate} - ${endDate}**\n\n`;

        if (exp.description) {
          markdown += `${exp.description}\n\n`;
        }

        if (exp.bullets.length > 0) {
          markdown += '**Responsibilities:**\n';
          exp.bullets.forEach(bullet => {
            markdown += `- ${bullet}\n`;
          });
          markdown += '\n';
        }

        if (exp.achievements.length > 0) {
          markdown += '**Key Achievements:**\n';
          exp.achievements.forEach(achievement => {
            markdown += `- ${achievement}\n`;
          });
          markdown += '\n';
        }

        if (exp.technologies.length > 0) {
          markdown += `**Technologies:** ${exp.technologies.join(', ')}\n\n`;
        }

        markdown += '---\n\n';
      });
    }

    // Education
    if (profileData.education.length > 0) {
      markdown += '## Education\n\n';
      profileData.education.forEach(edu => {
        markdown += `### ${edu.degree}`;
        if (edu.field) markdown += ` in ${edu.field}`;
        markdown += '\n';
        markdown += `**${edu.school}**\n`;

        const startDate = edu.startDate || '';
        const endDate = edu.endDate || '';
        if (startDate || endDate) {
          markdown += `**${startDate} - ${endDate}**\n`;
        }

        if (edu.gpa) markdown += `**GPA:** ${edu.gpa}`;
        if (edu.grade) markdown += ` • **Grade:** ${edu.grade}`;
        if (edu.gpa || edu.grade) markdown += '\n\n';

        if (edu.bullets && edu.bullets.length > 0) {
          markdown += '**Highlights:**\n';
          edu.bullets.forEach(bullet => {
            markdown += `- ${bullet}\n`;
          });
          markdown += '\n';
        }

        if (edu.honors && edu.honors.length > 0) {
          markdown += '**Honors & Awards:**\n';
          edu.honors.forEach(honor => {
            markdown += `- ${honor}\n`;
          });
          markdown += '\n';
        }

        if (edu.activities && edu.activities.length > 0) {
          markdown += '**Activities & Clubs:**\n';
          edu.activities.forEach(activity => {
            markdown += `- ${activity}\n`;
          });
          markdown += '\n';
        }

        markdown += '---\n\n';
      });
    }

    // Projects
    if (profileData.projects.length > 0) {
      markdown += '## Projects\n\n';
      profileData.projects.forEach(project => {
        markdown += `### ${project.name}\n\n`;

        if (project.description) {
          markdown += `${project.description}\n\n`;
        }

        if (project.bullets.length > 0) {
          markdown += '**Key Features/Contributions:**\n';
          project.bullets.forEach(bullet => {
            markdown += `- ${bullet}\n`;
          });
          markdown += '\n';
        }

        if (project.outcomes && project.outcomes.length > 0) {
          markdown += '**Outcomes & Impact:**\n';
          project.outcomes.forEach(outcome => {
            markdown += `- ${outcome}\n`;
          });
          markdown += '\n';
        }

        const projectDetails = [];
        if (project.startDate || project.endDate) {
          const start = project.startDate || '';
          const end = project.endDate || 'Present';
          projectDetails.push(`**Duration:** ${start} - ${end}`);
        }
        if (project.teamSize) projectDetails.push(`**Team Size:** ${project.teamSize}`);
        if (project.role) projectDetails.push(`**Role:** ${project.role}`);
        if (project.status) projectDetails.push(`**Status:** ${project.status}`);

        if (projectDetails.length > 0) {
          markdown += `${projectDetails.join(' • ')}\n\n`;
        }

        if (project.tech.length > 0) {
          markdown += `**Technologies:** ${project.tech.join(', ')}\n\n`;
        }

        markdown += '---\n\n';
      });
    }

    // Skills
    if (profileData.skills.length > 0) {
      markdown += '## Skills\n\n';

      // Group skills by category
      const skillsByCategory: { [key: string]: string[] } = {};
      profileData.skills.forEach(skill => {
        const category = skill.category || 'Technical Skills';
        if (!skillsByCategory[category]) {
          skillsByCategory[category] = [];
        }
        const skillText = skill.level ? `${skill.name} (${skill.level})` : skill.name;
        skillsByCategory[category].push(skillText);
      });

      Object.entries(skillsByCategory).forEach(([category, skills]) => {
        markdown += `### ${category}\n`;
        markdown += `${skills.join(' • ')}\n\n`;
      });
    }

    // Languages (detailed view)
    if (profileData.languages && profileData.languages.length > 0) {
      markdown += '## Languages\n\n';
      profileData.languages.forEach(lang => {
        const proficiency = lang.proficiency ? ` (${lang.proficiency})` : '';
        markdown += `- ${lang.name}${proficiency}\n`;
      });
      markdown += '\n';
    }

    return markdown;
  };

  const parseMarkdown = (markdown: string): ProfileData => {
    const lines = markdown.split('\n');
    const newProfile: ProfileData = {
      basics: { ...profile!.basics },
      work_experience: [],
      education: [],
      projects: [],
      skills: [],
      languages: []
    };

    let currentSection = '';
    let currentItem: any = null;
    let parsingBullets = false;
    let bulletType = '';

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      const nextLine = lines[i + 1]?.trim() || '';

      // Parse headers
      if (line.startsWith('# ')) {
        // Main title - skip
        continue;
      } else if (line.startsWith('## ')) {
        currentSection = line.substring(3).toLowerCase().replace(/\s+/g, '_');
        currentItem = null;
        parsingBullets = false;
        continue;
      } else if (line.startsWith('### ')) {
        const title = line.substring(4);

        // Create new item based on current section
        if (currentSection === 'work_experience') {
          currentItem = {
            company: '',
            title: title,
            startDate: '',
            endDate: null,
            location: '',
            employmentType: null,
            description: '',
            technologies: [],
            achievements: [],
            bullets: []
          };
          newProfile.work_experience.push(currentItem);
        } else if (currentSection === 'education') {
          currentItem = {
            school: '',
            degree: title,
            field: null,
            startDate: null,
            endDate: null,
            gpa: null,
            grade: null,
            honors: [],
            relevantCoursework: [],
            activities: [],
            thesis: null,
            bullets: []
          };
          newProfile.education.push(currentItem);
        } else if (currentSection === 'projects') {
          currentItem = {
            name: title,
            link: null,
            description: '',
            startDate: null,
            endDate: null,
            role: null,
            teamSize: null,
            status: null,
            outcomes: [],
            tech: [],
            bullets: []
          };
          newProfile.projects.push(currentItem);
        } else if (currentSection === 'skills') {
          // Skills are handled differently
          continue;
        }
        continue;
      }

      // Skip empty lines and separators
      if (!line || line === '---') continue;

      // Parse contact information
      if (currentSection === 'contact_information') {
        if (line.startsWith('📧')) {
          newProfile.basics.email = line.substring(2).trim();
        } else if (line.startsWith('📱')) {
          newProfile.basics.phone = line.substring(2).trim();
        } else if (line.startsWith('📍')) {
          newProfile.basics.location = line.substring(2).trim();
        }
        continue;
      }

      // Parse professional summary
      if (currentSection === 'professional_summary') {
        if (!newProfile.basics.summary) {
          newProfile.basics.summary = '';
        }
        if (line) {
          newProfile.basics.summary += (newProfile.basics.summary ? '\n' : '') + line;
        }
        continue;
      }

      // Parse languages
      if (currentSection === 'languages') {
        if (line.startsWith('- ')) {
          if (!newProfile.basics.languages) {
            newProfile.basics.languages = [];
          }
          newProfile.basics.languages.push(line.substring(2).trim());
        }
        continue;
      }

      // Parse work experience details
      if (currentSection === 'work_experience' && currentItem) {
        if (line.startsWith('**') && line.includes('**')) {
          const companyMatch = line.match(/\*\*([^*]+)\*\*/);
          if (companyMatch && !currentItem.company) {
            currentItem.company = companyMatch[1].split(',')[0].trim();
            const locationMatch = line.match(/, (.+)$/);
            if (locationMatch) {
              currentItem.location = locationMatch[1].trim();
            }
          }

          // Parse date range
          const dateMatch = line.match(/\*\*([^*]+ - [^*]+)\*\*/);
          if (dateMatch) {
            const dates = dateMatch[1].split(' - ');
            currentItem.startDate = dates[0].trim();
            currentItem.endDate = dates[1].trim() === 'Present' ? null : dates[1].trim();
          }
        } else if (line.startsWith('**Responsibilities:**')) {
          parsingBullets = true;
          bulletType = 'bullets';
        } else if (line.startsWith('**Key Achievements:**')) {
          parsingBullets = true;
          bulletType = 'achievements';
        } else if (line.startsWith('**Technologies:**')) {
          const techLine = line.substring(16);
          currentItem.technologies = techLine.split(',').map(t => t.trim()).filter(t => t);
        } else if (parsingBullets && line.startsWith('- ')) {
          const bullet = line.substring(2).trim();
          if (bulletType === 'bullets') {
            currentItem.bullets.push(bullet);
          } else if (bulletType === 'achievements') {
            currentItem.achievements.push(bullet);
          }
        } else if (parsingBullets && !line.startsWith('- ') && line.trim()) {
          // End of bullet list
          parsingBullets = false;
          bulletType = '';
        } else if (!parsingBullets && line && !line.startsWith('**')) {
          // Job description
          if (!currentItem.description) {
            currentItem.description = '';
          }
          currentItem.description += (currentItem.description ? '\n' : '') + line;
        }
        continue;
      }

      // Parse education details
      if (currentSection === 'education' && currentItem) {
        if (line.startsWith('**') && line.includes('**') && line.includes(',')) {
          const schoolMatch = line.match(/\*\*([^*]+)\*\*/);
          if (schoolMatch) {
            currentItem.school = schoolMatch[1].trim();
          }
        } else if (line.startsWith('**') && line.includes(' - ')) {
          const dates = line.replace(/\*\*/g, '').split(' - ');
          currentItem.startDate = dates[0].trim();
          currentItem.endDate = dates[1].trim();
        } else if (line.startsWith('**GPA:**')) {
          const gpaMatch = line.match(/(\d+\.?\d*)/);
          if (gpaMatch) {
            currentItem.gpa = parseFloat(gpaMatch[1]);
          }
        } else if (line.startsWith('- ')) {
          currentItem.bullets.push(line.substring(2).trim());
        } else if (line && !line.startsWith('**')) {
          // Additional description
          if (!currentItem.bullets.length) {
            currentItem.bullets = [];
          }
        }
        continue;
      }

      // Parse project details
      if (currentSection === 'projects' && currentItem) {
        if (line.startsWith('**Outcomes')) {
          parsingBullets = true;
          bulletType = 'outcomes';
        } else if (line.startsWith('**Technologies:**')) {
          const techLine = line.substring(16);
          currentItem.tech = techLine.split(',').map(t => t.trim()).filter(t => t);
        } else if (parsingBullets && line.startsWith('- ')) {
          const bullet = line.substring(2).trim();
          currentItem.outcomes.push(bullet);
        } else if (!parsingBullets && line.startsWith('- ')) {
          currentItem.bullets.push(line.substring(2).trim());
        } else if (!parsingBullets && line && !line.startsWith('**')) {
          // Project description
          if (!currentItem.description) {
            currentItem.description = '';
          }
          currentItem.description += (currentItem.description ? '\n' : '') + line;
        }
        continue;
      }

      // Parse skills
      if (currentSection === 'skills') {
        if (line.startsWith('### ')) {
          // Category header - skip for now, we'll handle categorization later
          continue;
        } else if (line.startsWith('- ') || line.includes(' • ')) {
          const skillsList = line.startsWith('- ') ? line.substring(2) : line;
          const skills = skillsList.split(' • ').map(s => s.trim());
          skills.forEach(skill => {
            if (skill) {
              // Parse skill level if present (e.g., "Python (advanced)")
              const levelMatch = skill.match(/(.+?)\s*\((.+?)\)/);
              if (levelMatch) {
                newProfile.skills.push({
                  name: levelMatch[1].trim(),
                  category: 'Technical Skills',
                  level: levelMatch[2] as any,
                  yearsExperience: null
                });
              } else {
                newProfile.skills.push({
                  name: skill,
                  category: 'Technical Skills',
                  level: null,
                  yearsExperience: null
                });
              }
            }
          });
        }
        continue;
      }

      // Parse detailed languages section
      if (currentSection === 'languages' && line.startsWith('- ')) {
        const langText = line.substring(2);
        const proficiencyMatch = langText.match(/(.+?)\s*\((.+?)\)/);
        if (proficiencyMatch) {
          newProfile.languages!.push({
            name: proficiencyMatch[1].trim(),
            proficiency: proficiencyMatch[2] as any
          });
        } else {
          newProfile.languages!.push({
            name: langText.trim(),
            proficiency: null
          });
        }
      }
    }

    return newProfile;
  };

  const handleMarkdownSave = () => {
    if (!markdownContent.trim()) return;

    try {
      const parsedProfile = parseMarkdown(markdownContent);
      setProfile(parsedProfile);
      setViewMode('form');
    } catch (err) {
      setError('Failed to parse markdown. Please check the format.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No profile found. Please upload your resume first.</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Review Your Resume Profile</h1>
                <p className="mt-1 text-sm text-gray-600">
                  AI extracted this information from your resume. Edit, add, or remove items as needed.
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setViewMode('form')}
                  className={`px-4 py-2 rounded-md text-sm font-medium ${
                    viewMode === 'form'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Form View
                </button>
                <button
                  onClick={() => {
                    if (profile) {
                      setMarkdownContent(generateMarkdown(profile));
                    }
                    setViewMode('markdown');
                  }}
                  className={`px-4 py-2 rounded-md text-sm font-medium ${
                    viewMode === 'markdown'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Markdown View
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="px-6 py-4 bg-red-50 border-b border-red-200">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          <div className="px-6 py-6">
            {viewMode === 'form' ? (
              <div className="space-y-8">
                {/* Basic Information */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">First Name</label>
                  <input
                    type="text"
                    value={profile.basics.firstName}
                    onChange={(e) => setProfile({
                      ...profile,
                      basics: { ...profile.basics, firstName: e.target.value }
                    })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Last Name</label>
                  <input
                    type="text"
                    value={profile.basics.lastName}
                    onChange={(e) => setProfile({
                      ...profile,
                      basics: { ...profile.basics, lastName: e.target.value }
                    })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    type="email"
                    value={profile.basics.email || ''}
                    onChange={(e) => setProfile({
                      ...profile,
                      basics: { ...profile.basics, email: e.target.value || null }
                    })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Phone</label>
                  <input
                    type="tel"
                    value={profile.basics.phone || ''}
                    onChange={(e) => setProfile({
                      ...profile,
                      basics: { ...profile.basics, phone: e.target.value || null }
                    })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Summary */}
              <div>
                <label className="block text-sm font-medium text-gray-700">Professional Summary</label>
                <textarea
                  value={profile.basics.summary || ''}
                  onChange={(e) => setProfile({
                    ...profile,
                    basics: { ...profile.basics, summary: e.target.value || null }
                  })}
                  rows={3}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Brief professional summary or objective..."
                />
              </div>

              {/* Languages */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-gray-700">Languages</label>
                  <button
                    onClick={addLanguage}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    + Add Language
                  </button>
                </div>
                <div className="space-y-2">
                  {(profile.basics.languages || []).map((language, index) => (
                    <div key={index} className="flex space-x-2">
                      <input
                        type="text"
                        value={language}
                        onChange={(e) => {
                          const newLanguages = [...(profile.basics.languages || [])];
                          newLanguages[index] = e.target.value;
                          setProfile({
                            ...profile,
                            basics: { ...profile.basics, languages: newLanguages }
                          });
                        }}
                        className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Language name"
                      />
                      <button
                        onClick={() => {
                          const newLanguages = (profile.basics.languages || []).filter((_, i) => i !== index);
                          setProfile({
                            ...profile,
                            basics: { ...profile.basics, languages: newLanguages.length > 0 ? newLanguages : null }
                          });
                        }}
                        className="text-red-600 hover:text-red-800 px-2"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Work Experience */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Work Experience</h2>
                <button
                  onClick={addWorkExperience}
                  className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
                >
                  Add Experience
                </button>
              </div>
              <div className="space-y-4">
                {profile.work_experience.map((exp, index) => (
                  <div key={index} className="border border-gray-200 rounded-md p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Company</label>
                        <input
                          type="text"
                          value={exp.company}
                          onChange={(e) => {
                            const newExp = [...profile.work_experience];
                            newExp[index].company = e.target.value;
                            setProfile({ ...profile, work_experience: newExp });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Title</label>
                        <input
                          type="text"
                          value={exp.title}
                          onChange={(e) => {
                            const newExp = [...profile.work_experience];
                            newExp[index].title = e.target.value;
                            setProfile({ ...profile, work_experience: newExp });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Start Date</label>
                        <input
                          type="text"
                          value={exp.startDate}
                          onChange={(e) => {
                            const newExp = [...profile.work_experience];
                            newExp[index].startDate = e.target.value;
                            setProfile({ ...profile, work_experience: newExp });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., January 2023 or 2023-01"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">End Date</label>
                        <input
                          type="text"
                          value={exp.endDate || ''}
                          onChange={(e) => {
                            const newExp = [...profile.work_experience];
                            newExp[index].endDate = e.target.value || null;
                            setProfile({ ...profile, work_experience: newExp });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., Present or December 2023"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Employment Type</label>
                        <select
                          value={exp.employmentType || ''}
                          onChange={(e) => {
                            const newExp = [...profile.work_experience];
                            newExp[index].employmentType = e.target.value || null;
                            setProfile({ ...profile, work_experience: newExp });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Select type</option>
                          <option value="full-time">Full-time</option>
                          <option value="part-time">Part-time</option>
                          <option value="contract">Contract</option>
                          <option value="freelance">Freelance</option>
                          <option value="internship">Internship</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Location</label>
                        <input
                          type="text"
                          value={exp.location || ''}
                          onChange={(e) => {
                            const newExp = [...profile.work_experience];
                            newExp[index].location = e.target.value || null;
                            setProfile({ ...profile, work_experience: newExp });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>

                    {/* Job Description */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Job Description</label>
                      <textarea
                        value={exp.description || ''}
                        onChange={(e) => {
                          const newExp = [...profile.work_experience];
                          newExp[index].description = e.target.value || null;
                          setProfile({ ...profile, work_experience: newExp });
                        }}
                        rows={2}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Brief overview of your role and responsibilities..."
                      />
                    </div>

                    {/* Technologies */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Technologies Used</label>
                      <input
                        type="text"
                        value={exp.technologies.join(', ')}
                        onChange={(e) => {
                          const newExp = [...profile.work_experience];
                          newExp[index].technologies = e.target.value.split(',').map(t => t.trim()).filter(t => t);
                          setProfile({ ...profile, work_experience: newExp });
                        }}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Python, React, Docker"
                      />
                    </div>

                    {/* Achievements */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Key Achievements</label>
                      <textarea
                        value={exp.achievements.join('\n')}
                        onChange={(e) => {
                          const newExp = [...profile.work_experience];
                          newExp[index].achievements = e.target.value.split('\n').filter(a => a.trim());
                          setProfile({ ...profile, work_experience: newExp });
                        }}
                        rows={3}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Increased performance by 40%&#10;Led team of 5 developers&#10;..."
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Education */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Education</h2>
                <button
                  onClick={addEducation}
                  className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
                >
                  Add Education
                </button>
              </div>
              <div className="space-y-4">
                {profile.education.map((edu, index) => (
                  <div key={index} className="border border-gray-200 rounded-md p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">School</label>
                        <input
                          type="text"
                          value={edu.school}
                          onChange={(e) => {
                            const newEdu = [...profile.education];
                            newEdu[index].school = e.target.value;
                            setProfile({ ...profile, education: newEdu });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Degree</label>
                        <input
                          type="text"
                          value={edu.degree}
                          onChange={(e) => {
                            const newEdu = [...profile.education];
                            newEdu[index].degree = e.target.value;
                            setProfile({ ...profile, education: newEdu });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Major/Field of Study</label>
                        <input
                          type="text"
                          value={edu.field || ''}
                          onChange={(e) => {
                            const newEdu = [...profile.education];
                            newEdu[index].field = e.target.value || null;
                            setProfile({ ...profile, education: newEdu });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., Computer Science"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Start Date</label>
                        <input
                          type="text"
                          value={edu.startDate || ''}
                          onChange={(e) => {
                            const newEdu = [...profile.education];
                            newEdu[index].startDate = e.target.value || null;
                            setProfile({ ...profile, education: newEdu });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., September 2020"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">End Date</label>
                        <input
                          type="text"
                          value={edu.endDate || ''}
                          onChange={(e) => {
                            const newEdu = [...profile.education];
                            newEdu[index].endDate = e.target.value || null;
                            setProfile({ ...profile, education: newEdu });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., May 2024"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">GPA</label>
                        <input
                          type="text"
                          value={edu.gpa || ''}
                          onChange={(e) => {
                            const newEdu = [...profile.education];
                            const gpaValue = e.target.value ? parseFloat(e.target.value) : null;
                            newEdu[index].gpa = gpaValue;
                            setProfile({ ...profile, education: newEdu });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., 3.8"
                        />
                      </div>
                    </div>

                    {/* Education Description */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Education Description</label>
                      <textarea
                        value={edu.bullets?.join('\n') || ''}
                        onChange={(e) => {
                          const newEdu = [...profile.education];
                          newEdu[index].bullets = e.target.value.split('\n').filter(b => b.trim());
                          setProfile({ ...profile, education: newEdu });
                        }}
                        rows={3}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Relevant coursework, honors, activities, thesis..."
                      />
                    </div>

                    {/* Honors and Activities */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Honors/Awards</label>
                        <textarea
                          value={edu.honors?.join('\n') || ''}
                          onChange={(e) => {
                            const newEdu = [...profile.education];
                            newEdu[index].honors = e.target.value.split('\n').filter(h => h.trim());
                            setProfile({ ...profile, education: newEdu });
                          }}
                          rows={2}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Dean's List, Summa Cum Laude..."
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Activities/Clubs</label>
                        <textarea
                          value={edu.activities?.join('\n') || ''}
                          onChange={(e) => {
                            const newEdu = [...profile.education];
                            newEdu[index].activities = e.target.value.split('\n').filter(a => a.trim());
                            setProfile({ ...profile, education: newEdu });
                          }}
                          rows={2}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Student Council, Computer Science Club..."
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Projects */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Projects</h2>
                <button
                  onClick={addProject}
                  className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
                >
                  Add Project
                </button>
              </div>
              <div className="space-y-4">
                {profile.projects.map((project, index) => (
                  <div key={index} className="border border-gray-200 rounded-md p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Project Name</label>
                        <input
                          type="text"
                          value={project.name}
                          onChange={(e) => {
                            const newProjects = [...profile.projects];
                            newProjects[index].name = e.target.value;
                            setProfile({ ...profile, projects: newProjects });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Role</label>
                        <input
                          type="text"
                          value={project.role || ''}
                          onChange={(e) => {
                            const newProjects = [...profile.projects];
                            newProjects[index].role = e.target.value || null;
                            setProfile({ ...profile, projects: newProjects });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., Lead Developer, Solo Developer"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Start Date</label>
                        <input
                          type="text"
                          value={project.startDate || ''}
                          onChange={(e) => {
                            const newProjects = [...profile.projects];
                            newProjects[index].startDate = e.target.value || null;
                            setProfile({ ...profile, projects: newProjects });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., January 2023"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">End Date</label>
                        <input
                          type="text"
                          value={project.endDate || ''}
                          onChange={(e) => {
                            const newProjects = [...profile.projects];
                            newProjects[index].endDate = e.target.value || null;
                            setProfile({ ...profile, projects: newProjects });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., March 2023 or Present"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Team Size</label>
                        <input
                          type="number"
                          value={project.teamSize || ''}
                          onChange={(e) => {
                            const newProjects = [...profile.projects];
                            const teamSizeValue = e.target.value ? parseInt(e.target.value) : null;
                            newProjects[index].teamSize = teamSizeValue;
                            setProfile({ ...profile, projects: newProjects });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., 5"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Status</label>
                        <select
                          value={project.status || ''}
                          onChange={(e) => {
                            const newProjects = [...profile.projects];
                            newProjects[index].status = e.target.value || null;
                            setProfile({ ...profile, projects: newProjects });
                          }}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Select status</option>
                          <option value="completed">Completed</option>
                          <option value="in-progress">In Progress</option>
                          <option value="on-hold">On Hold</option>
                        </select>
                      </div>
                    </div>

                    {/* Project Description */}
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700">Project Description</label>
                      <textarea
                        value={project.description}
                        onChange={(e) => {
                          const newProjects = [...profile.projects];
                          newProjects[index].description = e.target.value;
                          setProfile({ ...profile, projects: newProjects });
                        }}
                        rows={3}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Describe what the project was about, the problem it solved..."
                      />
                    </div>

                    {/* Technologies */}
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700">Technologies Used</label>
                      <input
                        type="text"
                        value={project.tech.join(', ')}
                        onChange={(e) => {
                          const newProjects = [...profile.projects];
                          newProjects[index].tech = e.target.value.split(',').map(t => t.trim()).filter(t => t);
                          setProfile({ ...profile, projects: newProjects });
                        }}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="React, Node.js, MongoDB, Docker"
                      />
                    </div>

                    {/* Outcomes */}
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700">Project Outcomes/Results</label>
                      <textarea
                        value={project.outcomes?.join('\n') || ''}
                        onChange={(e) => {
                          const newProjects = [...profile.projects];
                          newProjects[index].outcomes = e.target.value.split('\n').filter(o => o.trim());
                          setProfile({ ...profile, projects: newProjects });
                        }}
                        rows={2}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Increased user engagement by 40%&#10;Reduced loading time by 60%&#10;..."
                      />
                    </div>

                    {/* Detailed Bullets */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Detailed Contributions</label>
                      <textarea
                        value={project.bullets.join('\n')}
                        onChange={(e) => {
                          const newProjects = [...profile.projects];
                          newProjects[index].bullets = e.target.value.split('\n').filter(b => b.trim());
                          setProfile({ ...profile, projects: newProjects });
                        }}
                        rows={4}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="• Designed and implemented user authentication system&#10;• Built responsive UI components&#10;• Optimized database queries for better performance&#10;..."
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Skills */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Skills</h2>
                <button
                  onClick={addSkill}
                  className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
                >
                  Add Skill
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {profile.skills.map((skill, index) => (
                  <div key={index} className="border border-gray-200 rounded-md p-3">
                    <input
                      type="text"
                      value={skill.name}
                      onChange={(e) => {
                        const newSkills = [...profile.skills];
                        newSkills[index].name = e.target.value;
                        setProfile({ ...profile, skills: newSkills });
                      }}
                      className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Skill name"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Languages */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Languages</h2>
                <button
                  onClick={addLanguage}
                  className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
                >
                  Add Language
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(profile.languages || []).map((language, index) => (
                  <div key={index} className="border border-gray-200 rounded-md p-3">
                    <div className="flex space-x-2">
                      <div className="flex-1">
                        <input
                          type="text"
                          value={language.name}
                          onChange={(e) => {
                            const newLanguages = [...(profile.languages || [])];
                            newLanguages[index].name = e.target.value;
                            setProfile({ ...profile, languages: newLanguages });
                          }}
                          className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Language"
                        />
                      </div>
                      <div className="flex-1">
                        <select
                          value={language.proficiency || ''}
                          onChange={(e) => {
                            const newLanguages = [...(profile.languages || [])];
                            newLanguages[index].proficiency = e.target.value || null;
                            setProfile({ ...profile, languages: newLanguages });
                          }}
                          className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Select proficiency</option>
                          <option value="native">Native</option>
                          <option value="fluent">Fluent</option>
                          <option value="conversational">Conversational</option>
                          <option value="basic">Basic</option>
                        </select>
                      </div>
                      <button
                        onClick={() => {
                          const newLanguages = (profile.languages || []).filter((_, i) => i !== index);
                          setProfile({ ...profile, languages: newLanguages.length > 0 ? newLanguages : null });
                        }}
                        className="text-red-600 hover:text-red-800 px-2"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))}
              </div>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Resume in Markdown Format</h2>
                  <p className="text-sm text-gray-600 mb-4">
                    Edit your resume directly in markdown format. Use standard markdown syntax with headers, lists, and formatting.
                  </p>
                  <textarea
                    value={markdownContent}
                    onChange={(e) => setMarkdownContent(e.target.value)}
                    rows={40}
                    className="w-full border border-gray-300 rounded-md px-4 py-3 font-mono text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Write your resume in markdown format..."
                  />
                </div>

                <div className="flex space-x-4">
                  <button
                    onClick={() => setViewMode('form')}
                    className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
                  >
                    Back to Form View
                  </button>
                  <button
                    onClick={handleMarkdownSave}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                  >
                    Save Markdown Changes
                  </button>
                </div>
              </div>
            )}
          </div>

          {viewMode === 'form' && (
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
              <button
                onClick={() => router.push('/dashboard')}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
              >
                Back to Dashboard
              </button>
              <button
                onClick={saveProfile}
                disabled={saving}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-400"
              >
                {saving ? 'Saving...' : 'Save Profile'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}