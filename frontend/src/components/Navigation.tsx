'use client';

import React from 'react';
import {
  FileText,
  User,
  Briefcase,
  GitCompare,
  Sparkles,
  FileDown,
  Layers,
} from 'lucide-react';

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  profileName?: string;
}

export const Navigation: React.FC<NavigationProps> = ({
  activeTab,
  setActiveTab,
  profileName,
}) => {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Layers },
    { id: 'profile', label: 'Master Profile', icon: User },
    { id: 'jobs', label: 'Job Analysis', icon: Briefcase },
    { id: 'match', label: 'Match & Gaps', icon: GitCompare },
    { id: 'suggestions', label: 'AI Suggestions', icon: Sparkles },
    { id: 'resume', label: 'Customized Resume', icon: FileText },
    { id: 'versions', label: 'Saved Versions', icon: FileDown },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Identity */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-sky-500/20">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">
                  Customize Resume
                </span>
                <span className="bg-sky-100 text-sky-800 text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider">
                  Explainable AI
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Evidence-Grounded + Fact-Preserving
              </p>
            </div>
          </div>

          {/* User badge */}
          {profileName && (
            <div className="hidden lg:flex items-center space-x-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full text-xs text-slate-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span className="font-medium">Candidate: {profileName}</span>
            </div>
          )}
        </div>

        {/* Tab Navigation */}
        <nav className="flex space-x-1 overflow-x-auto py-2 border-t border-slate-100 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150 ${
                  isActive
                    ? 'bg-sky-600 text-white shadow-sm shadow-sky-600/30'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
