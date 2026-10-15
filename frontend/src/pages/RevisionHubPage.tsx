import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Brain,
  Sparkles,
  RotateCw,
  CheckCircle,
  AlertTriangle,
  BookOpen,
  Calendar,
  Layers,
  ArrowRight,
  ChevronRight,
  Flame,
  Check
} from 'lucide-react';
import { apiFetch } from '../lib/api';
import {
  WeaknessAnalysis,
  MistakeItem,
  Flashcard,
  DailyPlan,
  TestDetail
} from '../types';

export const RevisionHubPage: React.FC = () => {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<'weaknesses' | 'flashcards' | 'mistakes' | 'daily'>('weaknesses');
  const [weaknesses, setWeaknesses] = useState<WeaknessAnalysis | null>(null);
  const [mistakes, setMistakes] = useState<MistakeItem[]>([]);
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [dailyPlan, setDailyPlan] = useState<DailyPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [forging, setForging] = useState(false);

  // Flashcard Deck State
  const [currentCardIdx, setCurrentCardIdx] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  const fetchRevisionData = async () => {
    try {
      const [wData, mData, fData, dData] = await Promise.all([
        apiFetch<WeaknessAnalysis>('/revision/weaknesses'),
        apiFetch<MistakeItem[]>('/revision/mistakes'),
        apiFetch<Flashcard[]>('/revision/flashcards'),
        apiFetch<DailyPlan>('/revision/daily-plan'),
      ]);
      setWeaknesses(wData);
      setMistakes(mData);
      setFlashcards(fData);
      setDailyPlan(dData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRevisionData();
  }, []);

  const handleForgeTest = async () => {
    setForging(true);
    try {
      const test = await apiFetch<TestDetail>('/revision/forge-test', { method: 'POST' });
      navigate(`/exam/${test.id}`);
    } catch (err: any) {
      alert(err.message || 'Could not forge adaptive test');
    } finally {
      setForging(false);
    }
  };

  const handleReviewFlashcard = async (rating: number) => {
    if (flashcards.length === 0) return;
    const card = flashcards[currentCardIdx];
    try {
      await apiFetch(`/revision/flashcards/${card.id}/review`, {
        method: 'POST',
        body: JSON.stringify({ rating }),
      });
      // Move to next card
      setIsFlipped(false);
      if (currentCardIdx < flashcards.length - 1) {
        setCurrentCardIdx((prev) => prev + 1);
      } else {
        alert('Flashcard session completed for today!');
        setCurrentCardIdx(0);
        fetchRevisionData();
      }
    } catch (err: any) {
      alert('Failed to record review');
    }
  };

  const handleToggleResolveMistake = async (id: number, currentStatus: boolean) => {
    try {
      await apiFetch(`/revision/mistakes/${id}/resolve`, {
        method: 'PUT',
        body: JSON.stringify({ is_resolved: !currentStatus }),
      });
      setMistakes(
        mistakes.map((m) => (m.id === id ? { ...m, is_resolved: !currentStatus } : m))
      );
    } catch (err: any) {
      alert('Could not update status');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-violet-500" />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-16 selection:bg-violet-500 selection:text-white">
      {/* Top Banner */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6 border-violet-500/20">
        <div className="space-y-2 relative z-10">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">Adaptive Revision System</span>
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            <span className="text-xs text-gray-400">SuperMemo SM-2 & Error Analysis</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Revision Hub & Weakness Forge</h1>
          <p className="text-xs sm:text-sm text-gray-400 max-w-xl">
            Target topics where accuracy dipped below passing standards, flip spaced-repetition flashcards, and clear your mistake notebook.
          </p>
        </div>

        <button
          onClick={handleForgeTest}
          disabled={forging}
          className="relative z-10 px-5 py-3 rounded-2xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 disabled:opacity-50 text-white font-bold text-xs shadow-lg shadow-violet-500/25 flex items-center justify-center gap-2 transition-all group shrink-0"
        >
          <Sparkles className="w-4 h-4 text-cyan-300 group-hover:rotate-12 transition-transform" />
          <span>{forging ? 'Forging Targeted Test...' : 'Forge My Weaknesses (1-Click)'}</span>
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-white/5 pb-2 overflow-x-auto">
        {[
          { id: 'weaknesses', label: 'Weakness Analysis', icon: Brain, badge: weaknesses?.weakest_topics.length },
          { id: 'flashcards', label: 'Flashcard Deck', icon: Layers, badge: flashcards.length },
          { id: 'mistakes', label: 'Mistake Notebook', icon: AlertTriangle, badge: mistakes.filter((m) => !m.is_resolved).length },
          { id: 'daily', label: 'Daily Study Plan', icon: Calendar },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-violet-600/30 text-white border border-violet-500/40'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-gray-400'}`} />
              <span>{tab.label}</span>
              {typeof tab.badge === 'number' && (
                <span className={`px-1.5 py-0.2 rounded-md text-[10px] font-mono ${
                  isActive ? 'bg-violet-500 text-white' : 'bg-white/10 text-gray-400'
                }`}>
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Weakness Analysis */}
      {activeTab === 'weaknesses' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 rounded-2xl glass-panel border-rose-500/20 space-y-1">
              <span className="text-xs text-rose-400 font-semibold uppercase tracking-wider">Critical Weaknesses</span>
              <p className="text-2xl font-bold text-white">{weaknesses?.weakest_topics.length || 0}</p>
              <p className="text-[11px] text-gray-400">&lt;60% accuracy on past assessments</p>
            </div>
            <div className="p-5 rounded-2xl glass-panel border-amber-500/20 space-y-1">
              <span className="text-xs text-amber-400 font-semibold uppercase tracking-wider">Moderate Mastery</span>
              <p className="text-2xl font-bold text-white">{weaknesses?.moderate_topics.length || 0}</p>
              <p className="text-[11px] text-gray-400">60% - 80% accuracy tier</p>
            </div>
            <div className="p-5 rounded-2xl glass-panel border-emerald-500/20 space-y-1">
              <span className="text-xs text-emerald-400 font-semibold uppercase tracking-wider">Verified Strengths</span>
              <p className="text-2xl font-bold text-white">{weaknesses?.strong_topics.length || 0}</p>
              <p className="text-[11px] text-gray-400">&gt;80% mastery threshold</p>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white">Targeted Concepts for Adaptive Focus</h3>
            {weaknesses?.weakest_topics.length === 0 ? (
              <div className="p-8 rounded-2xl bg-white/5 text-center text-xs text-gray-400">
                No severe weaknesses detected! Keep taking challenging exams to stretch your skills.
              </div>
            ) : (
              weaknesses?.weakest_topics.map((w, idx) => (
                <div key={idx} className="glass-panel p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-rose-500/20">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white">{w.topic}</span>
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-500/30">
                        {w.accuracy_rate}% Accuracy
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">{w.recommended_focus}</p>
                  </div>

                  <button
                    onClick={handleForgeTest}
                    className="px-3.5 py-1.5 rounded-xl bg-violet-600/20 hover:bg-violet-600/30 border border-violet-500/30 text-xs font-semibold text-violet-300 transition-colors shrink-0"
                  >
                    Forge 5-Q Test
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Spaced Repetition Flashcards */}
      {activeTab === 'flashcards' && (
        <div className="max-w-2xl mx-auto space-y-6">
          {flashcards.length === 0 ? (
            <div className="glass-panel p-12 rounded-3xl text-center space-y-3">
              <Layers className="w-8 h-8 text-gray-500 mx-auto" />
              <h3 className="text-sm font-semibold text-gray-300">No Flashcards Due</h3>
              <p className="text-xs text-gray-500">
                Upload materials in Document Studio to auto-generate concept flashcards!
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Card {currentCardIdx + 1} of {flashcards.length}</span>
                <span className="font-mono text-cyan-400">Next Review: {flashcards[currentCardIdx].next_review_date}</span>
              </div>

              {/* 3D Flip Card */}
              <div
                onClick={() => setIsFlipped(!isFlipped)}
                className="w-full min-h-[280px] p-8 rounded-3xl glass-panel border-violet-500/30 cursor-pointer flex flex-col justify-between hover:border-violet-500/60 transition-all select-none relative overflow-hidden"
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="text-violet-400 font-semibold uppercase tracking-wider">
                    {flashcards[currentCardIdx].topic}
                  </span>
                  <span className="text-gray-500 text-[11px]">Click to Flip</span>
                </div>

                <div className="py-6 text-center">
                  {!isFlipped ? (
                    <h3 className="text-lg sm:text-xl font-bold text-white leading-relaxed">
                      {flashcards[currentCardIdx].front_prompt}
                    </h3>
                  ) : (
                    <div className="space-y-2">
                      <span className="text-[10px] uppercase font-bold text-cyan-400">Answer & Explanation</span>
                      <p className="text-sm sm:text-base text-gray-200 leading-relaxed font-sans">
                        {flashcards[currentCardIdx].back_explanation}
                      </p>
                    </div>
                  )}
                </div>

                <div className="text-center text-[11px] text-gray-500">
                  {isFlipped ? 'Showing Back Explanation' : 'Showing Front Prompt'}
                </div>
              </div>

              {/* Rating Buttons */}
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={() => handleReviewFlashcard(1)}
                  className="py-2.5 rounded-xl bg-rose-950/40 hover:bg-rose-950/60 border border-rose-500/30 text-rose-300 text-xs font-semibold transition-colors"
                >
                  Again (1d)
                </button>
                <button
                  onClick={() => handleReviewFlashcard(2)}
                  className="py-2.5 rounded-xl bg-violet-950/40 hover:bg-violet-950/60 border border-violet-500/30 text-violet-300 text-xs font-semibold transition-colors"
                >
                  Good (3d)
                </button>
                <button
                  onClick={() => handleReviewFlashcard(3)}
                  className="py-2.5 rounded-xl bg-emerald-950/40 hover:bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs font-semibold transition-colors"
                >
                  Easy (6d)
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Mistake Notebook */}
      {activeTab === 'mistakes' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">Logged Exam Errors</h3>
            <span className="text-xs text-gray-400">Auto-captured from all submitted exams</span>
          </div>

          {mistakes.length === 0 ? (
            <div className="glass-panel p-8 rounded-2xl text-center text-xs text-gray-400">
              No mistakes logged! Either you scored 100% or haven't taken a test yet.
            </div>
          ) : (
            <div className="space-y-3">
              {mistakes.map((m) => (
                <div
                  key={m.id}
                  className={`glass-panel p-5 rounded-2xl border space-y-3 transition-all ${
                    m.is_resolved ? 'opacity-60 border-emerald-500/20' : 'border-rose-500/30'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">{m.question_text}</span>
                        {m.is_resolved && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-500/30">
                            Resolved
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-gray-400 font-mono">
                        Topic: {m.topic_tag} • Source: {m.source_reference || 'Notes'}
                      </p>
                    </div>

                    <button
                      onClick={() => handleToggleResolveMistake(m.id, m.is_resolved)}
                      className={`p-2 rounded-xl border text-xs font-medium transition-all ${
                        m.is_resolved
                          ? 'bg-emerald-600/20 border-emerald-500/40 text-emerald-300'
                          : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'
                      }`}
                    >
                      {m.is_resolved ? 'Mark Unresolved' : 'Mark Understood'}
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
                    <div className="p-3 rounded-xl bg-white/5">
                      <span className="text-[10px] font-bold text-rose-400 uppercase">Your Wrong Choice:</span>
                      <p className="text-gray-300 mt-0.5">{m.user_wrong_answer || 'Skipped'}</p>
                    </div>
                    <div className="p-3 rounded-xl bg-white/5">
                      <span className="text-[10px] font-bold text-emerald-400 uppercase">Correct Answer:</span>
                      <p className="text-gray-300 mt-0.5">{m.correct_answer}</p>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/20 text-xs text-gray-300">
                    <span className="font-semibold text-cyan-300">Explanation: </span>
                    {m.explanation}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Daily Plan */}
      {activeTab === 'daily' && dailyPlan && (
        <div className="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 max-w-2xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs text-cyan-400 font-semibold">{dailyPlan.today_date}</span>
              <h2 className="text-xl font-bold text-white mt-1">{dailyPlan.greeting}</h2>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold">
              <Flame className="w-4 h-4" />
              <span>{dailyPlan.streak_count}-Day Streak</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white/5 border border-white/5 space-y-2">
            <span className="text-xs font-semibold text-violet-300">Primary Revision Focus Today</span>
            <p className="text-sm font-bold text-white">{dailyPlan.primary_revision_topic}</p>
            <p className="text-xs text-gray-400">Target study session: {dailyPlan.target_study_minutes} minutes</p>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-300">Today's Action Items</h4>
            {dailyPlan.recommended_actions.map((act, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-violet-600/30 border border-violet-500/40 text-violet-300 flex items-center justify-center font-bold text-xs">
                    {idx + 1}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-white">{act.title}</p>
                    <p className="text-[10px] text-gray-400">Est. {act.estimated_mins} mins</p>
                  </div>
                </div>

                <button
                  onClick={() => {
                    if (act.type === 'forge_test') handleForgeTest();
                    else if (act.type === 'flashcards') setActiveTab('flashcards');
                    else setActiveTab('mistakes');
                  }}
                  className="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-cyan-300 transition-colors"
                >
                  Start
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
