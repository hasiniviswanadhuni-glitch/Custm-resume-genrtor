'use client';

import React from 'react';
import { ResumeVersion } from '../lib/types';
import { api } from '../lib/api';
import { Download, FileText, CheckCircle2, Shield } from 'lucide-react';

interface ResumePreviewProps {
  version: ResumeVersion;
}

export const ResumePreview: React.FC<ResumePreviewProps> = ({ version }) => {
  const content = version.tailored_content;

  const handleDownloadPDF = () => {
    window.open(api.getPDFUrl(version.id), '_blank');
  };

  const handleDownloadDOCX = () => {
    window.open(api.getDOCXUrl(version.id), '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-bold text-slate-900">{version.title}</h3>
            <span className="bg-emerald-100 text-emerald-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">
              ATS Score: {version.ats_score}%
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 flex items-center space-x-1.5">
            <Shield className="w-3.5 h-3.5 text-sky-600" />
            <span>
              Derived Job-Specific Version. Master profile was not modified.
            </span>
            <span className="text-slate-300">•</span>
            <span>{content.applied_suggestions_count} suggestions incorporated</span>
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleDownloadPDF}
            className="flex items-center space-x-2 px-4 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-xl shadow-sm shadow-sky-600/20 transition"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF</span>
          </button>
          <button
            onClick={handleDownloadDOCX}
            className="flex items-center space-x-2 px-4 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-white border border-slate-300 hover:bg-slate-50 rounded-xl transition"
          >
            <FileText className="w-4 h-4 text-sky-600" />
            <span>Download DOCX</span>
          </button>
        </div>
      </div>

      {/* Printable / Viewable Resume Document */}
      <div className="bg-white rounded-2xl border border-slate-200 p-8 sm:p-12 shadow-sm max-w-4xl mx-auto font-sans text-slate-800 space-y-6">
        {/* Header */}
        <div className="text-center border-b border-slate-200 pb-5">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 uppercase">
            {content.full_name}
          </h1>
          <div className="text-xs text-slate-500 mt-1 flex flex-wrap justify-center items-center gap-x-3 gap-y-1">
            {content.email && <span>{content.email}</span>}
            {content.phone && <span>• {content.phone}</span>}
            {content.location && <span>• {content.location}</span>}
            {content.linkedin_url && <span>• {content.linkedin_url}</span>}
            {content.github_url && <span>• {content.github_url}</span>}
          </div>
        </div>

        {/* Summary */}
        {content.professional_summary && (
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-1 mb-2">
              Professional Summary
            </h2>
            <p className="text-xs leading-relaxed text-slate-700">
              {content.professional_summary}
            </p>
          </div>
        )}

        {/* Skills */}
        {content.skills && content.skills.length > 0 && (
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-1 mb-2">
              Core Skills & Technologies
            </h2>
            <p className="text-xs leading-relaxed text-slate-700">
              {content.skills.map((s) => s.name).join(', ')}
            </p>
          </div>
        )}

        {/* Work Experience */}
        {content.experience && content.experience.length > 0 && (
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-1 mb-3">
              Work Experience
            </h2>
            <div className="space-y-4">
              {content.experience.map((exp, i) => (
                <div key={i} className="text-xs">
                  <div className="flex justify-between items-baseline font-semibold text-slate-900">
                    <span>
                      {exp.position} — {exp.company}
                    </span>
                    <span className="text-[11px] text-slate-500 font-normal">
                      {exp.start_date} – {exp.end_date || 'Present'}
                    </span>
                  </div>
                  {exp.bullets && exp.bullets.length > 0 && (
                    <ul className="list-disc list-outside pl-4 mt-1.5 space-y-1 text-slate-700">
                      {exp.bullets.map((b, bIdx) => (
                        <li key={bIdx}>{b}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Technical Projects */}
        {content.projects && content.projects.length > 0 && (
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-1 mb-3">
              Technical Projects
            </h2>
            <div className="space-y-4">
              {content.projects.map((proj, i) => (
                <div key={i} className="text-xs">
                  <div className="flex justify-between items-baseline font-semibold text-slate-900">
                    <div>
                      <span>{proj.title}</span>
                      {proj.technologies && proj.technologies.length > 0 && (
                        <span className="text-slate-500 font-normal text-[11px] ml-2">
                          [{proj.technologies.join(', ')}]
                        </span>
                      )}
                    </div>
                    {proj.start_date && (
                      <span className="text-[11px] text-slate-500 font-normal">
                        {proj.start_date} – {proj.end_date || 'Completed'}
                      </span>
                    )}
                  </div>
                  {proj.bullets && proj.bullets.length > 0 && (
                    <ul className="list-disc list-outside pl-4 mt-1.5 space-y-1 text-slate-700">
                      {proj.bullets.map((b, bIdx) => (
                        <li key={bIdx}>{b}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Education */}
        {content.education && content.education.length > 0 && (
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-1 mb-2">
              Education
            </h2>
            <div className="space-y-2">
              {content.education.map((edu, i) => (
                <div key={i} className="flex justify-between text-xs">
                  <div>
                    <span className="font-semibold text-slate-900">
                      {edu.degree} in {edu.field_of_study || 'Computer Science'}
                    </span>{' '}
                    — <span>{edu.institution}</span>
                    {edu.gpa && (
                      <span className="text-slate-500 text-[11px] ml-2">
                        (GPA: {edu.gpa})
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] text-slate-500">
                    {edu.start_date} – {edu.end_date}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Certifications */}
        {content.certifications && content.certifications.length > 0 && (
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-1 mb-2">
              Certifications
            </h2>
            <ul className="list-disc list-outside pl-4 text-xs space-y-1 text-slate-700">
              {content.certifications.map((c, i) => (
                <li key={i}>
                  <span className="font-medium text-slate-900">{c.name}</span>{' '}
                  — {c.issuer}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
