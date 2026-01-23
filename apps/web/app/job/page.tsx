'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { apiClient } from '../../lib/api'

export default function JobPage() {
  const searchParams = useSearchParams()
  const jobUrl = searchParams.get('jobUrl') || ''
  const [jobData, setJobData] = useState<any>(null)
  const [tailoringData, setTailoringData] = useState<any>(null)
  const [profileStatus, setProfileStatus] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [availableTemplates, setAvailableTemplates] = useState<any>({})
  const [selectedTemplate, setSelectedTemplate] = useState<string>('modern-professional')

  // Get profile info from API
  const profileId = profileStatus?.profileId

  // Helper function for authenticated downloads
  const downloadFile = async (url: string, filename: string) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      alert('Session expired. Please log in again.');
      window.location.href = '/login';
      return;
    }

    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(blobUrl);
        document.body.removeChild(a);
      } else if (response.status === 401) {
        alert('Session expired. Please log in again.');
        window.location.href = '/login';
      } else {
        alert('Download failed. Please try again.');
      }
    } catch (error) {
      alert('Download failed. Please try again.');
    }
  }

  useEffect(() => {
    const loadProfileAndProcessJob = async () => {
      if (!jobUrl) {
        setError('No job URL provided')
        setIsLoading(false)
        return
      }

      // Fetch available templates
      try {
        const templates = await apiClient.get('/v1/tailor/templates');
        setAvailableTemplates(templates);
      } catch (err) {
        console.error('Failed to fetch templates:', err);
      }

      try {
        setIsLoading(true)

        // Step 1: Load profile status
        const profileResult = await apiClient.get('/v1/profile/me')
        setProfileStatus(profileResult)

        // Step 2: Ingest the job
        console.log('Ingesting job:', jobUrl)
        const jobResult = await apiClient.post('/v1/jobs/ingest', { url: jobUrl })
        console.log('Job ingested:', jobResult)
        setJobData(jobResult)

        // Step 3: If we have a profile, tailor the resume
        if (profileResult.hasProfile && jobResult.job_posting?.id) {
          console.log('Tailoring resume for job:', jobResult.job_posting.id, 'profile:', profileResult.profileId)
          try {
            const tailoringResult = await apiClient.post(`/v1/tailor?template_id=${selectedTemplate}`, {
              job_id: jobResult.job_posting.id,
              profile_id: profileResult.profileId,
            })
            console.log('Tailoring completed:', tailoringResult)
            setTailoringData(tailoringResult)
          } catch (error) {
            console.warn('Tailoring failed:', error)
            // Don't throw error for tailoring - it's optional
          }
        }

      } catch (err) {
        console.error('Error processing job:', err)
        setError(err instanceof Error ? err.message : 'Failed to process job posting')
      } finally {
        setIsLoading(false)
      }
    }

    loadProfileAndProcessJob()
  }, [jobUrl])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Analyzing job posting...</p>
          <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-red-900 mb-4">Error Processing Job</h2>
          <p className="text-red-700 mb-6">{error}</p>
          <button
            onClick={() => window.history.back()}
            className="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {jobData.job_posting?.title || 'Job Title'}
          </h1>
          <p className="text-xl text-gray-600 mb-4">{jobData.job_posting?.company_name || 'Company'}</p>
          <p className="text-gray-500">{jobData.job_posting?.location || 'Location not specified'}</p>
          <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500">
            <span>Provider: {jobData.job_posting?.provider || 'Unknown'}</span>
            <span>•</span>
            <span>URL: {jobData.job_posting?.source_url ? (
              <a href={jobData.job_posting.source_url} target="_blank" rel="noopener noreferrer"
                 className="text-blue-600 hover:underline">
                View Original
              </a>
            ) : 'N/A'}</span>
          </div>
        </div>

        {/* Job Description */}
        {jobData.job_posting?.description_text && (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Job Description
            </h2>
            <p className="text-gray-700 whitespace-pre-line">{jobData.job_posting.description_text}</p>
          </div>
        )}

        {/* HTML Description */}
        {jobData.job_posting?.description_html && (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Full Job Description
            </h2>
            <div
              className="text-gray-700 prose max-w-none"
              dangerouslySetInnerHTML={{ __html: jobData.job_posting.description_html }}
            />
          </div>
        )}

        {/* Application Form Fields */}
        {jobData.job_posting?.application_form_schema && jobData.job_posting.application_form_schema.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Application Form Fields
            </h2>
            <div className="space-y-3">
              {jobData.job_posting.application_form_schema.map((field: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded">
                  <div>
                    <span className="font-medium">{field.label}</span>
                    <span className="text-sm text-gray-500 ml-2">({field.type})</span>
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </div>
                  {field.options && field.options.length > 0 && (
                    <span className="text-sm text-gray-600">
                      {field.options.length} options
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Raw Extraction Info */}
        {jobData.job_posting?.raw && (
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Extraction Details</h3>
            <div className="text-sm text-gray-600 space-y-1">
              <p>Extraction Method: {jobData.job_posting.raw.extraction_path || 'Unknown'}</p>
              <p>Processed: {jobData.job_posting.raw.fetched_at ? new Date(jobData.job_posting.raw.fetched_at).toLocaleString() : 'Unknown'}</p>
              {jobData.job_posting.raw.warnings && jobData.job_posting.raw.warnings.length > 0 && (
                <div>
                  <p className="text-orange-600">Warnings:</p>
                  <ul className="list-disc list-inside ml-4">
                    {jobData.job_posting.raw.warnings.map((warning: string, index: number) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tailored Results */}
        {tailoringData ? (
          <div className="space-y-8">
            {/* Summary */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Job Analysis Summary
              </h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Job Summary</h3>
                  <p className="text-gray-700 text-sm">{tailoringData.jd_summary}</p>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Required Skills</h3>
                  <p className="text-gray-700 text-sm">{tailoringData.skills_required}</p>
                </div>
              </div>
            </div>

            {/* Suggested Bullets */}
            {tailoringData.suggested_bullets && tailoringData.suggested_bullets.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                  Suggested Resume Bullets
                </h2>
                <ul className="space-y-2">
                  {tailoringData.suggested_bullets.map((bullet: any, index: number) => (
                    <li key={index} className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span className="text-gray-700">{bullet.tailored}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Cover Letter */}
            {tailoringData.cover_letter_text && (
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                  Generated Cover Letter
                </h2>
                <div className="bg-gray-50 p-4 rounded whitespace-pre-line text-gray-700">
                  {tailoringData.cover_letter_text}
                </div>
              </div>
            )}

            {/* Template Selector */}
            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Choose Resume Template</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(availableTemplates).map(([templateId, template]: [string, any]) => (
                  <div
                    key={templateId}
                    className={`border-2 rounded-lg p-6 cursor-pointer transition-all hover:shadow-md ${
                      selectedTemplate === templateId
                        ? 'border-blue-500 bg-blue-50 shadow-md'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedTemplate(templateId)}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900">{template.name}</h3>
                      {selectedTemplate === templateId && (
                        <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                    <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                      template.style === 'modern' ? 'bg-blue-100 text-blue-800' :
                      template.style === 'classic' ? 'bg-gray-100 text-gray-800' :
                      template.style === 'minimal' ? 'bg-teal-100 text-teal-800' :
                      template.style === 'tech' ? 'bg-purple-100 text-purple-800' :
                      'bg-orange-100 text-orange-800'
                    }`}>
                      {template.style === 'modern' ? '💼' :
                       template.style === 'classic' ? '📜' :
                       template.style === 'minimal' ? '🎨' :
                       template.style === 'tech' ? '💻' : '🎓'} {template.style}
                    </div>
                    {templateId === 'modern-professional' && (
                      <p className="text-xs text-gray-500 mt-2">Most Popular</p>
                    )}
                  </div>
                ))}
              </div>
              <p className="text-sm text-gray-500 mt-4">
                💡 Select a template style that matches your industry and experience level
              </p>
            </div>

            {/* Downloads */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Download Your Tailored Application
              </h2>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <h3 className="font-medium text-gray-900">Tailored Resume (DOCX)</h3>
                    <p className="text-sm text-gray-600">Customized for this job</p>
                  </div>
                  <button
                    onClick={() => downloadFile(tailoringData.tailored_resume_docx_url, 'tailored_resume.docx')}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  >
                    Download
                  </button>
                </div>


                {tailoringData.cover_letter_docx_url && (
                  <div className="flex items-center justify-between p-4 border border-red-200 bg-red-50 rounded-lg">
                    <div>
                      <h3 className="font-medium text-red-900">Cover Letter (DOCX)</h3>
                      <p className="text-sm text-red-700">Personalized for this application</p>
                    </div>
                    <button
                      onClick={() => downloadFile(tailoringData.cover_letter_docx_url, 'cover_letter.docx')}
                      className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                    >
                      Download
                    </button>
                  </div>
                )}

                {tailoringData.application_package_docx_url && (
                  <div className="flex items-center justify-between p-4 border border-green-200 bg-green-50 rounded-lg">
                    <div>
                      <h3 className="font-medium text-green-900">Complete Application Package</h3>
                      <p className="text-sm text-green-700">Resume + Cover Letter + Application Summary</p>
                    </div>
                    <button
                      onClick={() => downloadFile(tailoringData.application_package_docx_url, 'Application_Package.zip')}
                      className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                    >
                      Download All
                    </button>
                  </div>
                )}

                <div className="flex items-center justify-between p-4 border border-green-200 bg-green-50 rounded-lg">
                  <div>
                    <h3 className="font-medium text-green-900">Open & Autofill Application</h3>
                    <p className="text-sm text-green-700">Ready to apply with autofilled answers</p>
                  </div>
                  <button
                    onClick={() => {
                      if (jobData?.apply_url) {
                        window.open(jobData.apply_url, '_blank');
                      } else {
                        alert('Apply URL not available. Please use the job posting link directly.');
                      }
                    }}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                  >
                    Apply Now
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Resume Processing Required
            </h2>

            <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
              <h3 className="font-medium text-yellow-900">Resume Not Processed</h3>
              <p className="text-sm text-yellow-700 mt-1">
                {!profileStatus?.hasProfile
                  ? "You need to upload your resume first to generate tailored documents and autofill answers."
                  : "Your resume is being processed. Please wait for tailoring to complete."
                }
              </p>
              {!profileStatus?.hasProfile ? (
                <button
                  onClick={() => window.location.href = `/dashboard?jobUrl=${encodeURIComponent(jobUrl)}`}
                  className="mt-3 bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700 text-sm"
                >
                  Upload Resume First
                </button>
              ) : (
                <p className="text-sm text-gray-600 mt-2">
                  Processing your resume for this job...
                </p>
              )}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}