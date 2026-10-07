'use client';

import React from 'react';
import { ATSScoreBreakdown } from '../lib/types';
import { Info, CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';

interface MatchRadarProps {
  scoreBreakdown: ATSScoreBreakdown;
  jobTitle: string;
}

export const MatchRadar: React.FC<MatchRadarProps> = ({
  scoreBreakdown,
  jobTitle,
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 60) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-rose-600 bg-rose-50 border-rose-200';
  };

  const getBarColor = (score: number) => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const factors = [
    {
      label: 'Technical Skills Overlap',
      score: scoreBreakdown.technical_skills,
      weight: '35%',
      desc: scoreBreakdown.calculation_details?.technical_skills || 'Matches against target technical stack.',
    },
    {
      label: 'Keyword Presence',
      score: scoreBreakdown.keyword_match,
      weight: '25%',
      desc: scoreBreakdown.calculation_details?.keyword_match || 'Presence of core JD terminology in profile.',
    },
    {
      label: 'Project Relevance',
      score: scoreBreakdown.project_relevance,
      weight: '20%',
      desc: scoreBreakdown.calculation_details?.project_relevance || 'Coverage of required tech in candidate projects.',
    },
    {
      label: 'Experience Relevance',
      score: scoreBreakdown.experience_relevance,
      weight: '10%',
      desc: scoreBreakdown.calculation_details?.experience_relevance || 'Years and role alignment with seniority targets.',
    },
    {
      label: 'Education Alignment',
      score: scoreBreakdown.education_match,
      weight: '10%',
      desc: scoreBreakdown.calculation_details?.education_match || 'Degree level and STEM specialization match.',
    },
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-sky-600">
            Transparent ATS Analysis
          </span>
          <h3 className="text-xl font-bold text-slate-900 mt-0.5">
            Target Match: {jobTitle}
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Calculated via documented, deterministic formula. Zero arbitrary AI numbers.
          </p>
        </div>

        {/* Overall Match Circle / Pill */}
        <div className={`flex items-center space-x-3 px-5 py-3 rounded-2xl border ${getScoreColor(scoreBreakdown.overall_score)}`}>
          <div className="text-right">
            <span className="text-[11px] font-semibold uppercase tracking-wider block">
              Overall Score
            </span>
            <span className="text-2xl font-black">
              {scoreBreakdown.overall_score}%
            </span>
          </div>
          {scoreBreakdown.overall_score >= 75 ? (
            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
          ) : (
            <AlertCircle className="w-8 h-8 text-amber-600" />
          )}
        </div>
      </div>

      {/* Breakdown Factors Grid */}
      <div className="mt-6 space-y-4">
        {factors.map((f, i) => (
          <div key={i} className="bg-slate-50 rounded-xl p-3.5 border border-slate-100">
            <div className="flex justify-between items-center text-xs mb-1.5">
              <div className="flex items-center space-x-1.5">
                <span className="font-semibold text-slate-800">{f.label}</span>
                <span className="text-[10px] text-slate-400 bg-white border border-slate-200 px-1.5 py-0.2 rounded font-mono">
                  Weight: {f.weight}
                </span>
              </div>
              <span className="font-bold text-slate-900 text-sm">{f.score}%</span>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${getBarColor(f.score)}`}
                style={{ width: `${f.score}%` }}
              ></div>
            </div>

            <p className="text-[11px] text-slate-500 mt-2 flex items-start space-x-1">
              <Info className="w-3.5 h-3.5 text-slate-400 mt-0.5 shrink-0" />
              <span>{f.desc}</span>
            </p>
          </div>
        ))}
      </div>

      {/* Formula Documentation Card */}
      <div className="mt-5 bg-sky-50 border border-sky-100 rounded-xl p-3 text-xs text-sky-900">
        <span className="font-semibold block mb-0.5">Formula Audit Trail:</span>
        <code className="text-[11px] text-sky-800 font-mono block">
          {scoreBreakdown.calculation_details?.formula ||
            'Overall = (Technical * 0.35) + (Keywords * 0.25) + (Projects * 0.20) + (Experience * 0.10) + (Education * 0.10)'}
        </code>
      </div>
    </div>
  );
};
