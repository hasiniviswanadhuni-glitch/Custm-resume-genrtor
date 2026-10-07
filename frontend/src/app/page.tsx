'use client';

import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import {
  CandidateProfile,
  JobDescription,
  MatchAnalysis,
  AISuggestion,
  ResumeVersion,
} from '../lib/types';
import { Navigation } from '../components/Navigation';
import { MatchRadar } from '../components/MatchRadar';
import { SuggestionCard } from '../components/SuggestionCard';
import { ResumePreview } from '../components/ResumePreview';
import {
  Sparkles,
  FileText,
  Briefcase,
  CheckCircle2,
  AlertCircle,
  Plus,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  ChevronRight,
  TrendingUp,
  Download,
  Trash2,
  AlertTriangle,
} from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [jobs, setJobs] = useState<JobDescription[]>([]);
  const [selectedJob, setSelectedJob] = useState<JobDescription | null>(null);
  const [matchAnalysis, setMatchAnalysis] = useState<MatchAnalysis | null>(null);
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [resumeVersions, setResumeVersions] = useState<ResumeVersion[]>([]);
  const [activeResume, setActiveResume] = useState<ResumeVersion | null>(null);

  // Form states
  const [jobTitleInput, setJobTitleInput] = useState('');
  const [jobCompanyInput, setJobCompanyInput] = useState('');
  const [jobTextInput, setJobTextInput] = useState('');
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState('technical');
  const [newSkillProf, setNewSkillProf] = useState('intermediate');

  // Status and feedback
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Initial Data Load
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const p = await api.getProfile();
      setProfile(p);

      const j = await api.getJobs();
      setJobs(j);
      if (j.length > 0) {
        setSelectedJob(j[0]);
      }

      const r = await api.getResumeVersions();
      setResumeVersions(r);
      if (r.length > 0) {
        setActiveResume(r[0]);
      }
    } catch (err: any) {
      console.error('Failed to load initial data:', err);
      setErrorMessage(err.message || 'Failed to connect to backend service.');
    } finally {
      setIsLoading(false);
    }
  };

  // Seed Demo Profile
  const handleSeedDemoProfile = async () => {
    setActionLoading('seed-profile');
    try {
      const p = await api.seedDemoProfile();
      setProfile(p);
      setSuccessMessage('Loaded demo student/graduate candidate profile.');
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: any) {
      setErrorMessage('Failed to seed demo profile: ' + err.message);
    } finally {
      setActionLoading(null);
    }
  };

  // Seed Demo Job
  const handleSeedDemoJob = async () => {
    setActionLoading('seed-job');
    try {
      const j = await api.seedDemoJob();
      setJobs((prev) => [j, ...prev.filter((item) => item.id !== j.id)]);
      setSelectedJob(j);
      setSuccessMessage('Loaded demo job description: Software Engineer (Python & Full Stack).');
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: any) {
      setErrorMessage('Failed to seed demo job: ' + err.message);
    } finally {
      setActionLoading(null);
    }
  };

  // Create & Analyze Custom Job
  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTextInput || jobTextInput.length < 20) {
      setErrorMessage('Please enter at least 20 characters of job description.');
      return;
    }
    setActionLoading('analyze-job');
    try {
      const created = await api.createJob({
        title: jobTitleInput || 'Target Position',
        company: jobCompanyInput || 'Hiring Company',
        raw_text: jobTextInput,
      });
      setJobs((prev) => [created, ...prev]);
      setSelectedJob(created);
      setJobTitleInput('');
      setJobCompanyInput('');
      setJobTextInput('');
      setSuccessMessage('Job description analyzed and saved successfully.');
      setTimeout(() => setSuccessMessage(null), 4000);
      setActiveTab('match');
      // Auto run match
      if (profile) {
        handleRunMatch(profile.id, created.id);
      }
    } catch (err: any) {
      setErrorMessage('Failed to analyze job: ' + err.message);
    } finally {
      setActionLoading(null);
    }
  };

  // Run Match Analysis
  const handleRunMatch = async (pId: string, jId: string) => {
    setActionLoading('match');
    try {
      const res = await api.runMatch(pId, jId);
      setMatchAnalysis(res);
      // Auto load suggestions
      const suggs = await api.getSuggestions(jId);
      setSuggestions(suggs);
    } catch (err: any) {
      setErrorMessage('Match analysis failed: ' + err.message);
    } finally {
      setActionLoading(null);
    }
  };

  // Update Suggestion Action
  const handleUpdateSuggestion = async (
    sugId: string,
    status: 'accepted' | 'rejected' | 'edited' | 'pending',
    editedText?: string
  ) => {
    try {
      const updated = await api.updateSuggestion(sugId, { status, edited_text: editedText });
      setSuggestions((prev) =>
        prev.map((s) => (s.id === sugId ? updated : s))
      );
    } catch (err: any) {
      setErrorMessage('Failed to update suggestion: ' + err.message);
    }
  };

  // Customize Resume
  const handleCustomizeResume = async () => {
    if (!profile || !selectedJob) return;
    setActionLoading('customize');
    try {
      const customized = await api.customizeResume(
        profile.id,
        selectedJob.id,
        `${selectedJob.title} — Tailored Resume`
      );
      setResumeVersions((prev) => [customized, ...prev]);
      setActiveResume(customized);
      setSuccessMessage('Job-specific resume derived successfully! Master profile is preserved.');
      setTimeout(() => setSuccessMessage(null), 5000);
      setActiveTab('resume');
    } catch (err: any) {
      setErrorMessage('Failed to generate customized resume: ' + err.message);
    } finally {
      setActionLoading(null);
    }
  };

  // Add Skill to Master Profile
  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillName.trim() || !profile) return;
    const updatedSkills = [
      ...profile.skills,
      {
        name: newSkillName.trim(),
        category: newSkillCategory,
        proficiency_level: newSkillProf,
      },
    ];
    try {
      const updatedProfile = await api.updateProfile({ skills: updatedSkills });
      setProfile(updatedProfile);
      setNewSkillName('');
      setSuccessMessage(`Added "${newSkillName.trim()}" to Master Profile.`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setErrorMessage('Failed to add skill: ' + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans pb-24 text-slate-900">
      <Navigation
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        profileName={profile?.full_name}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {/* Global Notifications */}
        {errorMessage && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-xs font-semibold hover:underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>{successMessage}</span>
            </div>
            <button
              onClick={() => setSuccessMessage(null)}
              className="text-xs font-semibold hover:underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 1: DASHBOARD                                         */}
        {/* ======================================================== */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {/* Hero Banner */}
            <div className="bg-gradient-to-r from-sky-900 via-indigo-900 to-slate-900 rounded-3xl p-8 sm:p-10 text-white shadow-xl relative overflow-hidden">
              <div className="relative z-10 max-w-3xl">
                <span className="bg-sky-400/20 text-sky-200 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider inline-flex items-center space-x-1 mb-4 border border-sky-400/30">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Truthful & Explainable Customization</span>
                </span>
                <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight leading-tight">
                  Tailor your resume to any job description without fabricating facts.
                </h1>
                <p className="mt-3 text-sm sm:text-base text-slate-300 leading-relaxed">
                  Analyze your candidate qualifications against job requirements, inspect transparent ATS scores, review explainable AI recommendations, and export ATS-compliant resumes with verified evidence.
                </p>

                <div className="mt-6 flex flex-wrap gap-3">
                  <button
                    onClick={() => setActiveTab('jobs')}
                    className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs shadow-md transition"
                  >
                    <Briefcase className="w-4 h-4" />
                    <span>Analyze Target Job</span>
                  </button>
                  <button
                    onClick={() => setActiveTab('profile')}
                    className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-medium text-xs border border-white/20 transition"
                  >
                    <span>View Master Profile</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Metrics Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Master Profile Skills</span>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {profile?.skills.length || 0}
                </div>
                <div className="text-[11px] text-emerald-600 font-semibold mt-1 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Verified Candidate Evidence</span>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Saved Target Jobs</span>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {jobs.length}
                </div>
                <div className="text-[11px] text-sky-600 font-semibold mt-1">
                  {selectedJob ? selectedJob.title : 'None selected'}
                </div>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">AI Suggestions</span>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {suggestions.length}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  {suggestions.filter((s) => s.status === 'accepted').length} Accepted / {suggestions.filter((s) => s.status === 'rejected').length} Rejected
                </div>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Derived Resumes</span>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {resumeVersions.length}
                </div>
                <div className="text-[11px] text-indigo-600 font-semibold mt-1">
                  PDF & DOCX Ready
                </div>
              </div>
            </div>

            {/* Workflow Progression Stepper */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">
                Recommended 6-Step Customization Journey
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {[
                  { step: '1', title: 'Master Profile', desc: 'Maintain truthful candidate facts', tab: 'profile' },
                  { step: '2', title: 'Target Job', desc: 'Paste & extract requirements', tab: 'jobs' },
                  { step: '3', title: 'Match & Gaps', desc: 'Deterministic ATS analysis', tab: 'match' },
                  { step: '4', title: 'AI Suggestions', desc: 'Review explainable optimizations', tab: 'suggestions' },
                  { step: '5', title: 'Derive Resume', desc: 'Generate customized snapshot', tab: 'resume' },
                  { step: '6', title: 'Export', desc: 'Download PDF or Word DOCX', tab: 'resume' },
                ].map((s) => (
                  <div
                    key={s.step}
                    onClick={() => setActiveTab(s.tab)}
                    className="p-4 rounded-xl border border-slate-100 bg-slate-50 hover:bg-sky-50/50 hover:border-sky-200 cursor-pointer transition"
                  >
                    <span className="w-6 h-6 rounded-full bg-sky-600 text-white font-bold text-xs flex items-center justify-center mb-2">
                      {s.step}
                    </span>
                    <h4 className="font-bold text-xs text-slate-900">{s.title}</h4>
                    <p className="text-[11px] text-slate-500 mt-1">{s.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 2: MASTER PROFILE                                    */}
        {/* ======================================================== */}
        {activeTab === 'profile' && profile && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <div>
                <span className="text-xs font-semibold text-sky-600 uppercase tracking-wider">
                  Source of Truth
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-0.5">
                  Master Candidate Profile
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  This profile stores all verified candidate facts. It is NEVER overwritten during resume tailoring.
                </p>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  onClick={handleSeedDemoProfile}
                  disabled={actionLoading === 'seed-profile'}
                  className="flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 rounded-xl transition disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${actionLoading === 'seed-profile' ? 'animate-spin' : ''}`} />
                  <span>Seed Demo Profile</span>
                </button>
              </div>
            </div>

            {/* Profile Information Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Personal info & Summary */}
              <div className="lg:col-span-1 space-y-6">
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">
                    Personal Information
                  </h3>
                  <div className="space-y-3 text-xs">
                    <div>
                      <span className="text-slate-400 block">Full Name</span>
                      <span className="font-semibold text-slate-800 text-sm">{profile.full_name}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Email</span>
                      <span className="font-medium text-slate-800">{profile.email}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Phone</span>
                      <span className="font-medium text-slate-800">{profile.phone || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Location</span>
                      <span className="font-medium text-slate-800">{profile.location || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">LinkedIn</span>
                      <span className="font-medium text-sky-600 truncate block">{profile.linkedin_url || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">GitHub</span>
                      <span className="font-medium text-sky-600 truncate block">{profile.github_url || 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Professional Summary */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">
                    Master Summary
                  </h3>
                  <p className="text-xs leading-relaxed text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100">
                    {profile.professional_summary || 'No summary provided.'}
                  </p>
                </div>
              </div>

              {/* Right Column: Skills, Projects, Experience */}
              <div className="lg:col-span-2 space-y-6">
                {/* Skills Manager */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">
                    Verified Skills ({profile.skills.length})
                  </h3>

                  {/* Add Skill Form */}
                  <form onSubmit={handleAddSkill} className="flex flex-wrap gap-2 mb-4">
                    <input
                      type="text"
                      placeholder="Add a genuine skill (e.g., Docker, Go)..."
                      value={newSkillName}
                      onChange={(e) => setNewSkillName(e.target.value)}
                      className="px-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 grow"
                    />
                    <select
                      value={newSkillCategory}
                      onChange={(e) => setNewSkillCategory(e.target.value)}
                      className="px-2 py-1.5 text-xs border border-slate-300 rounded-lg"
                    >
                      <option value="technical">Technical</option>
                      <option value="tool">Tool</option>
                      <option value="domain">Domain</option>
                      <option value="soft">Soft</option>
                    </select>
                    <button
                      type="submit"
                      className="px-3 py-1.5 bg-sky-600 text-white font-medium text-xs rounded-lg hover:bg-sky-700 shadow-sm"
                    >
                      Add Skill
                    </button>
                  </form>

                  {/* Skills Badges */}
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.map((s, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200"
                      >
                        <span>{s.name}</span>
                        <span className="text-[10px] text-slate-400 capitalize">({s.proficiency_level})</span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Projects */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">
                    Verified Technical Projects ({profile.projects.length})
                  </h3>
                  <div className="space-y-4">
                    {profile.projects.map((p, i) => (
                      <div key={i} className="p-4 rounded-xl border border-slate-100 bg-slate-50 text-xs">
                        <div className="flex justify-between items-baseline font-bold text-slate-900">
                          <span>{p.title}</span>
                          <span className="font-normal text-slate-400 text-[11px]">{p.role}</span>
                        </div>
                        <p className="text-slate-600 mt-1">{p.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {p.technologies.map((t, tIdx) => (
                            <span key={tIdx} className="bg-sky-100 text-sky-800 px-2 py-0.5 rounded text-[10px] font-mono">
                              {t}
                            </span>
                          ))}
                        </div>
                        <ul className="list-disc pl-4 mt-2 space-y-1 text-slate-600">
                          {p.bullets.map((b, bIdx) => (
                            <li key={bIdx}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Experience & Education */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">
                      Work Experience
                    </h3>
                    {profile.experience.map((e, i) => (
                      <div key={i} className="text-xs mb-3 pb-3 border-b border-slate-100 last:border-none last:mb-0">
                        <span className="font-bold text-slate-900 block">{e.position}</span>
                        <span className="text-slate-500">{e.company} ({e.start_date} – {e.end_date || 'Present'})</span>
                      </div>
                    ))}
                  </div>

                  <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">
                      Education
                    </h3>
                    {profile.education.map((ed, i) => (
                      <div key={i} className="text-xs mb-3 pb-3 border-b border-slate-100 last:border-none last:mb-0">
                        <span className="font-bold text-slate-900 block">{ed.degree} in {ed.field_of_study}</span>
                        <span className="text-slate-500">{ed.institution} ({ed.start_date} – {ed.end_date})</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 3: JOB ANALYSIS                                      */}
        {/* ======================================================== */}
        {activeTab === 'jobs' && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <div>
                <span className="text-xs font-semibold text-sky-600 uppercase tracking-wider">
                  Target Job Input
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-0.5">
                  Job Description Analysis
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Extracts technical skills, soft skills, education, responsibilities, and key terminology.
                </p>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  onClick={handleSeedDemoJob}
                  disabled={actionLoading === 'seed-job'}
                  className="flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 rounded-xl transition"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${actionLoading === 'seed-job' ? 'animate-spin' : ''}`} />
                  <span>Load Sample Full-Stack Job</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Input Form */}
              <div className="lg:col-span-1 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">
                  Paste Target Job
                </h3>
                <form onSubmit={handleCreateJob} className="space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Job Title</label>
                    <input
                      type="text"
                      placeholder="e.g. Senior Python Engineer"
                      value={jobTitleInput}
                      onChange={(e) => setJobTitleInput(e.target.value)}
                      className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Company (Optional)</label>
                    <input
                      type="text"
                      placeholder="e.g. Stripe, TechCorp"
                      value={jobCompanyInput}
                      onChange={(e) => setJobCompanyInput(e.target.value)}
                      className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Job Description Text *</label>
                    <textarea
                      rows={10}
                      placeholder="Paste the full job posting here..."
                      value={jobTextInput}
                      onChange={(e) => setJobTextInput(e.target.value)}
                      className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={actionLoading === 'analyze-job'}
                    className="w-full py-2.5 text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 rounded-xl shadow-md transition disabled:opacity-50"
                  >
                    {actionLoading === 'analyze-job' ? 'Analyzing with NLP...' : 'Analyze & Save Job'}
                  </button>
                </form>
              </div>

              {/* Parsed Output & Saved Jobs List */}
              <div className="lg:col-span-2 space-y-6">
                {/* Saved jobs selector */}
                {jobs.length > 0 && (
                  <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                    <span className="text-xs font-bold text-slate-900 uppercase tracking-wider block mb-3">
                      Select Target Job ({jobs.length} Available)
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {jobs.map((j) => (
                        <button
                          key={j.id}
                          onClick={() => {
                            setSelectedJob(j);
                            if (profile) handleRunMatch(profile.id, j.id);
                          }}
                          className={`px-3 py-2 rounded-xl text-xs font-medium border text-left transition ${
                            selectedJob?.id === j.id
                              ? 'bg-sky-50 border-sky-400 text-sky-900 font-semibold ring-2 ring-sky-500/20'
                              : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                          }`}
                        >
                          <div>{j.title}</div>
                          <div className="text-[10px] text-slate-400">{j.company || 'Company'}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Extracted Requirements View */}
                {selectedJob && (
                  <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
                    <div className="flex justify-between items-baseline border-b border-slate-100 pb-3">
                      <div>
                        <h3 className="text-lg font-bold text-slate-900">{selectedJob.title}</h3>
                        <p className="text-xs text-slate-500">{selectedJob.company || 'Hiring Organization'}</p>
                      </div>
                      <button
                        onClick={() => {
                          setActiveTab('match');
                          if (profile) handleRunMatch(profile.id, selectedJob.id);
                        }}
                        className="flex items-center space-x-1.5 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold shadow-sm"
                      >
                        <span>Run Match Analysis</span>
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Extracted Technical Skills */}
                    <div>
                      <span className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2">
                        Extracted Technical Requirements ({selectedJob.parsed_data?.technical_skills?.length || 0})
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {selectedJob.parsed_data?.technical_skills?.map((t, i) => (
                          <span key={i} className="bg-sky-50 border border-sky-200 text-sky-800 px-2.5 py-1 rounded-lg text-xs font-medium">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Extracted Soft Skills */}
                    <div>
                      <span className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2">
                        Extracted Soft Skills ({selectedJob.parsed_data?.soft_skills?.length || 0})
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {selectedJob.parsed_data?.soft_skills?.map((s, i) => (
                          <span key={i} className="bg-indigo-50 border border-indigo-200 text-indigo-800 px-2.5 py-1 rounded-lg text-xs font-medium">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Extracted Responsibilities */}
                    {selectedJob.parsed_data?.responsibilities?.length > 0 && (
                      <div>
                        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2">
                          Key Role Responsibilities
                        </span>
                        <ul className="list-disc pl-4 text-xs space-y-1.5 text-slate-600">
                          {selectedJob.parsed_data.responsibilities.map((r, i) => (
                            <li key={i}>{r}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 4: MATCH & GAP ANALYSIS                              */}
        {/* ======================================================== */}
        {activeTab === 'match' && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <div>
                <span className="text-xs font-semibold text-sky-600 uppercase tracking-wider">
                  Two-Level Semantic & Keyword Match
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-0.5">
                  Candidate vs Job Description Match
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Categorized into Exact, Related, Partial, and Missing requirements with factual evidence citations.
                </p>
              </div>

              {profile && selectedJob && (
                <button
                  onClick={() => handleRunMatch(profile.id, selectedJob.id)}
                  disabled={actionLoading === 'match'}
                  className="flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-xl shadow-sm transition disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${actionLoading === 'match' ? 'animate-spin' : ''}`} />
                  <span>Re-compute Match</span>
                </button>
              )}
            </div>

            {matchAnalysis ? (
              <div className="space-y-6">
                {/* Transparent ATS Radar Component */}
                <MatchRadar
                  scoreBreakdown={matchAnalysis.score_breakdown}
                  jobTitle={matchAnalysis.job_title}
                />

                {/* Categorized Matches Breakdown Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* 1. Exact Matches (Green) */}
                  <div className="bg-white rounded-2xl border border-emerald-200 p-5 shadow-sm">
                    <div className="flex items-center space-x-2 text-emerald-800 mb-3">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <h4 className="font-bold text-xs uppercase tracking-wider">
                        Exact Matches ({matchAnalysis.exact_matches.length})
                      </h4>
                    </div>
                    <div className="space-y-2.5">
                      {matchAnalysis.exact_matches.map((m, i) => (
                        <div key={i} className="p-2.5 bg-emerald-50/60 rounded-xl text-xs border border-emerald-100">
                          <span className="font-bold text-emerald-900 block">{m.requirement_name}</span>
                          <span className="text-[11px] text-emerald-700 mt-1 block">{m.candidate_evidence}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 2. Related Capabilities (Blue) */}
                  <div className="bg-white rounded-2xl border border-sky-200 p-5 shadow-sm">
                    <div className="flex items-center space-x-2 text-sky-800 mb-3">
                      <TrendingUp className="w-4 h-4 text-sky-600" />
                      <h4 className="font-bold text-xs uppercase tracking-wider">
                        Related Matches ({matchAnalysis.related_matches.length})
                      </h4>
                    </div>
                    <div className="space-y-2.5">
                      {matchAnalysis.related_matches.map((m, i) => (
                        <div key={i} className="p-2.5 bg-sky-50/60 rounded-xl text-xs border border-sky-100">
                          <span className="font-bold text-sky-900 block">{m.requirement_name}</span>
                          <span className="text-[11px] text-sky-700 mt-1 block">{m.candidate_evidence}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 3. Partial Matches (Amber) */}
                  <div className="bg-white rounded-2xl border border-amber-200 p-5 shadow-sm">
                    <div className="flex items-center space-x-2 text-amber-800 mb-3">
                      <AlertCircle className="w-4 h-4 text-amber-600" />
                      <h4 className="font-bold text-xs uppercase tracking-wider">
                        Partial Matches ({matchAnalysis.partial_matches.length})
                      </h4>
                    </div>
                    <div className="space-y-2.5">
                      {matchAnalysis.partial_matches.map((m, i) => (
                        <div key={i} className="p-2.5 bg-amber-50/60 rounded-xl text-xs border border-amber-100">
                          <span className="font-bold text-amber-900 block">{m.requirement_name}</span>
                          <span className="text-[11px] text-amber-700 mt-1 block">{m.explanation}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 4. Missing Requirements (Red) */}
                  <div className="bg-white rounded-2xl border border-rose-200 p-5 shadow-sm">
                    <div className="flex items-center space-x-2 text-rose-800 mb-3">
                      <AlertTriangle className="w-4 h-4 text-rose-600" />
                      <h4 className="font-bold text-xs uppercase tracking-wider">
                        Missing Skills ({matchAnalysis.missing_requirements.length})
                      </h4>
                    </div>
                    <div className="space-y-2.5">
                      {matchAnalysis.missing_requirements.map((m, i) => (
                        <div key={i} className="p-2.5 bg-rose-50/60 rounded-xl text-xs border border-rose-100">
                          <span className="font-bold text-rose-900 block">{m.requirement_name}</span>
                          <span className="text-[10px] text-rose-700 mt-1 block">
                            Fact preservation: Zero evidence in candidate profile. Not fabricated.
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={() => setActiveTab('suggestions')}
                    className="flex items-center space-x-2 px-6 py-2.5 bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs rounded-xl shadow-md transition"
                  >
                    <span>Proceed to AI Suggestions</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500">
                <p>Select a job description and click "Run Match Analysis" to inspect qualifications.</p>
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 5: EXPLAINABLE AI SUGGESTIONS                         */}
        {/* ======================================================== */}
        {activeTab === 'suggestions' && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <div>
                <span className="text-xs font-semibold text-sky-600 uppercase tracking-wider">
                  Fact-Preserving Recommendations
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-0.5">
                  Explainable AI Suggestions
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Every suggestion shows the reason, target requirement, and candidate evidence. You have complete control to Accept, Reject, or Edit.
                </p>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  onClick={handleCustomizeResume}
                  disabled={actionLoading === 'customize'}
                  className="flex items-center space-x-1.5 px-5 py-2.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-md transition disabled:opacity-50"
                >
                  <FileText className="w-4 h-4" />
                  <span>Derive Customized Resume</span>
                </button>
              </div>
            </div>

            {/* Suggestions List */}
            {suggestions.length > 0 ? (
              <div className="space-y-4">
                {suggestions.map((sug) => (
                  <SuggestionCard
                    key={sug.id}
                    suggestion={sug}
                    onUpdateStatus={handleUpdateSuggestion}
                  />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500">
                <p>No suggestions generated yet. Select a job and run Match Analysis first.</p>
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 6: CUSTOMIZED RESUME PREVIEW & EXPORT                */}
        {/* ======================================================== */}
        {activeTab === 'resume' && (
          <div className="space-y-6">
            {activeResume ? (
              <ResumePreview version={activeResume} />
            ) : (
              <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500">
                <p>No tailored resume generated yet. Complete the suggestions review and click "Derive Customized Resume".</p>
                <button
                  onClick={handleCustomizeResume}
                  className="mt-4 px-4 py-2 bg-sky-600 text-white font-semibold text-xs rounded-xl shadow-sm"
                >
                  Derive Resume Now
                </button>
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 7: SAVED VERSIONS                                    */}
        {/* ======================================================== */}
        {activeTab === 'versions' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold text-sky-600 uppercase tracking-wider">
                Document History
              </span>
              <h2 className="text-xl font-bold text-slate-900 mt-0.5">
                Saved Job-Specific Resumes ({resumeVersions.length})
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Each version is derived independently for specific roles while the Master Profile remains untouched.
              </p>
            </div>

            {resumeVersions.length > 0 ? (
              <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[11px]">
                    <tr>
                      <th className="p-4">Resume Title</th>
                      <th className="p-4">Target Role</th>
                      <th className="p-4">ATS Match</th>
                      <th className="p-4">Suggestions Applied</th>
                      <th className="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-800">
                    {resumeVersions.map((v) => (
                      <tr key={v.id} className="hover:bg-slate-50 transition">
                        <td className="p-4 font-bold text-slate-900">{v.title}</td>
                        <td className="p-4 text-slate-600">{v.target_role || 'Target Role'}</td>
                        <td className="p-4 font-bold text-emerald-600">{v.ats_score}%</td>
                        <td className="p-4 text-slate-600">{v.tailored_content?.applied_suggestions_count || 0}</td>
                        <td className="p-4 text-right space-x-2">
                          <button
                            onClick={() => {
                              setActiveResume(v);
                              setActiveTab('resume');
                            }}
                            className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-md font-medium"
                          >
                            Preview
                          </button>
                          <a
                            href={api.getPDFUrl(v.id)}
                            target="_blank"
                            rel="noreferrer"
                            className="px-3 py-1 bg-sky-600 hover:bg-sky-700 text-white rounded-md font-medium"
                          >
                            PDF
                          </a>
                          <a
                            href={api.getDOCXUrl(v.id)}
                            target="_blank"
                            rel="noreferrer"
                            className="px-3 py-1 bg-slate-800 hover:bg-slate-900 text-white rounded-md font-medium"
                          >
                            DOCX
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500">
                <p>No saved versions found.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
