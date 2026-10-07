'use client';

import React, { useState } from 'react';
import { AISuggestion } from '../lib/types';
import {
  Check,
  X,
  Edit3,
  HelpCircle,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  RotateCcw,
} from 'lucide-react';

interface SuggestionCardProps {
  suggestion: AISuggestion;
  onUpdateStatus: (
    id: string,
    status: 'accepted' | 'rejected' | 'edited' | 'pending',
    editedText?: string
  ) => void;
}

export const SuggestionCard: React.FC<SuggestionCardProps> = ({
  suggestion,
  onUpdateStatus,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(
    suggestion.edited_text || suggestion.suggested_text
  );

  const getSectionBadgeColor = (sec: string) => {
    switch (sec) {
      case 'summary':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'skills':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'projects':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'experience':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const getStatusBadge = () => {
    switch (suggestion.status) {
      case 'accepted':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <Check className="w-3.5 h-3.5" />
            <span>Accepted</span>
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200">
            <X className="w-3.5 h-3.5" />
            <span>Rejected</span>
          </span>
        );
      case 'edited':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 border border-indigo-200">
            <Edit3 className="w-3.5 h-3.5" />
            <span>Custom Edited</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
            <span>Pending Review</span>
          </span>
        );
    }
  };

  const handleSaveEdit = () => {
    onUpdateStatus(suggestion.id, 'edited', editText);
    setIsEditing(false);
  };

  return (
    <div
      className={`rounded-2xl border transition-all duration-200 p-5 ${
        suggestion.status === 'accepted'
          ? 'bg-emerald-50/40 border-emerald-300 shadow-sm'
          : suggestion.status === 'rejected'
          ? 'bg-slate-50/60 border-slate-200 opacity-60'
          : suggestion.status === 'edited'
          ? 'bg-indigo-50/40 border-indigo-300 shadow-sm'
          : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
      }`}
    >
      {/* Header */}
      <div className="flex justify-between items-start gap-3">
        <div className="flex items-center space-x-2">
          <span
            className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md border ${getSectionBadgeColor(
              suggestion.target_section
            )}`}
          >
            {suggestion.target_section}
          </span>
          <span className="text-xs text-slate-400 font-mono">
            Confidence: {Math.round(suggestion.confidence_score * 100)}%
          </span>
        </div>

        <div className="flex items-center space-x-2">{getStatusBadge()}</div>
      </div>

      {/* Suggestion Text & Original Comparison */}
      <div className="mt-4">
        {suggestion.original_text && (
          <div className="mb-3 text-xs bg-slate-100/70 rounded-xl p-3 border border-slate-200 text-slate-600">
            <span className="font-semibold text-slate-500 block text-[10px] uppercase tracking-wider mb-1">
              Original Content
            </span>
            <p className="line-through decoration-slate-400 text-slate-600">
              {suggestion.original_text}
            </p>
          </div>
        )}

        <div className="text-xs bg-white rounded-xl p-3.5 border border-sky-100 shadow-sm">
          <span className="font-bold text-sky-800 text-[10px] uppercase tracking-wider block mb-1 flex items-center space-x-1">
            <Sparkles className="w-3.5 h-3.5 text-sky-600" />
            <span>Recommended Optimization</span>
          </span>

          {isEditing ? (
            <div className="mt-2 space-y-2">
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                rows={3}
                className="w-full text-xs text-slate-800 p-2.5 border border-sky-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 font-sans"
              />
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-3 py-1 text-xs text-slate-600 hover:text-slate-900 border border-slate-200 rounded-md"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEdit}
                  className="px-3 py-1 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-md shadow-sm"
                >
                  Save & Apply
                </button>
              </div>
            </div>
          ) : (
            <p className="text-slate-800 font-medium leading-relaxed">
              {suggestion.status === 'edited' && suggestion.edited_text
                ? suggestion.edited_text
                : suggestion.suggested_text}
            </p>
          )}
        </div>
      </div>

      {/* Explainability Breakdown (The "Why" and Evidence) */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
        <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100">
          <span className="font-semibold text-slate-700 block mb-0.5">
            Why this matters:
          </span>
          <p className="text-slate-600">{suggestion.reason}</p>
        </div>

        <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100">
          <span className="font-semibold text-slate-700 block mb-0.5">
            Triggered by Job Requirement:
          </span>
          <p className="text-slate-600 font-mono text-[10px]">
            {suggestion.job_requirement}
          </p>
        </div>
      </div>

      <div className="mt-2 bg-emerald-50/60 border border-emerald-100 rounded-lg p-2.5 text-[11px] flex items-start space-x-2">
        <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-emerald-900 block">
            Supporting Candidate Evidence:
          </span>
          <p className="text-emerald-800">{suggestion.candidate_evidence}</p>
        </div>
      </div>

      {/* Action Controls */}
      <div className="mt-5 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
        <div className="text-[11px] text-slate-400">
          Candidate controls all changes.
        </div>

        <div className="flex items-center space-x-2">
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center space-x-1 px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-100 border border-slate-200 rounded-lg transition"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Edit</span>
            </button>
          )}

          {suggestion.status !== 'rejected' && (
            <button
              onClick={() => onUpdateStatus(suggestion.id, 'rejected')}
              className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-50 border border-rose-200 rounded-lg transition"
            >
              <X className="w-3.5 h-3.5" />
              <span>Reject</span>
            </button>
          )}

          {suggestion.status !== 'accepted' && (
            <button
              onClick={() => onUpdateStatus(suggestion.id, 'accepted')}
              className="flex items-center space-x-1 px-3 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Accept</span>
            </button>
          )}

          {suggestion.status !== 'pending' && (
            <button
              onClick={() => onUpdateStatus(suggestion.id, 'pending')}
              title="Reset to Pending"
              className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg border border-slate-100 hover:bg-slate-50 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
