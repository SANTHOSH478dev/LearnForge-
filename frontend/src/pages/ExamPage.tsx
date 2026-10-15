import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Timer,
  CheckCircle2,
  Bookmark,
  ChevronLeft,
  ChevronRight,
  Maximize2,
  Minimize2,
  AlertTriangle,
  Send,
  Sparkles,
  HelpCircle,
  FileCheck2
} from 'lucide-react';
import { apiFetch } from '../lib/api';
import { AttemptStartData, AttemptResultData } from '../types';

export const ExamPage: React.FC = () => {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();

  const [examData, setExamData] = useState<AttemptStartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [reviewMarked, setReviewMarked] = useState<number[]>([]);
  const [secondsRemaining, setSecondsRemaining] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [autosaveStatus, setAutosaveStatus] = useState<string>('Connected');

  const timerRef = useRef<any>(null);

  // 1. Start or resume attempt
  useEffect(() => {
    const startExam = async () => {
      try {
        const data = await apiFetch<AttemptStartData>(`/tests/${testId}/start`, { method: 'POST' });
        setExamData(data);
        setAnswers(data.saved_answers || {});
        setReviewMarked(data.marked_for_review || []);

        // Compute seconds remaining from server deadline
        const deadlineMs = new Date(data.server_deadline).getTime();
        const nowMs = new Date().getTime();
        const diffSecs = Math.max(0, Math.floor((deadlineMs - nowMs) / 1000));
        setSecondsRemaining(diffSecs);
      } catch (err: any) {
        alert(err.message || 'Failed to initialize exam');
        navigate('/tests/create');
      } finally {
        setLoading(false);
      }
    };
    startExam();
  }, [testId, navigate]);

  // 2. Countdown timer loop
  useEffect(() => {
    if (!examData || secondsRemaining <= 0) return;

    timerRef.current = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          handleForceSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [examData]);

  const handleForceSubmit = async () => {
    if (isSubmitting || !examData) return;
    setIsSubmitting(true);
    try {
      const res = await apiFetch<AttemptResultData>(`/attempts/${examData.attempt_id}/submit`, {
        method: 'POST',
        body: JSON.stringify({ answers }),
      });
      navigate(`/attempts/${res.attempt_id}/results`);
    } catch (err: any) {
      console.error(err);
      navigate('/dashboard');
    }
  };

  const handleSelectOption = async (optionKey: string) => {
    if (!examData) return;
    const currentQ = examData.questions[currentIdx];
    const qidStr = currentQ.id.toString();

    // Toggle if clicking same option
    const newSelected = answers[qidStr] === optionKey ? '' : optionKey;
    const newAnswers = { ...answers, [qidStr]: newSelected };
    setAnswers(newAnswers);

    // Autosave to server
    setAutosaveStatus('Saving...');
    try {
      await apiFetch(`/attempts/${examData.attempt_id}/answers/${currentQ.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          selected_option_key: newSelected || null,
          is_marked_for_review: reviewMarked.includes(currentQ.id),
        }),
      });
      setAutosaveStatus('Autosaved');
    } catch (err) {
      setAutosaveStatus('Offline');
    }
  };

  const handleToggleMarkForReview = async () => {
    if (!examData) return;
    const currentQ = examData.questions[currentIdx];
    let newMarked: number[];

    if (reviewMarked.includes(currentQ.id)) {
      newMarked = reviewMarked.filter((id) => id !== currentQ.id);
    } else {
      newMarked = [...reviewMarked, currentQ.id];
    }
    setReviewMarked(newMarked);

    try {
      await apiFetch(`/attempts/${examData.attempt_id}/answers/${currentQ.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          is_marked_for_review: newMarked.includes(currentQ.id),
        }),
      });
    } catch {
      // ignore
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
      setIsFullscreen(true);
    } else {
      document.exitFullscreen().catch(() => {});
      setIsFullscreen(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh]">
        <div className="text-center space-y-3">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyan-400 mx-auto" />
          <p className="text-xs text-gray-400">Loading Exam Arena and verifying server deadline...</p>
        </div>
      </div>
    );
  }

  if (!examData) return null;

  const currentQ = examData.questions[currentIdx];
  const qidStr = currentQ.id.toString();
  const selectedOpt = answers[qidStr];
  const isMarked = reviewMarked.includes(currentQ.id);

  const formatTimer = (totalSecs: number) => {
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const isTimeCritical = secondsRemaining < 120; // under 2 mins

  const answeredCount = Object.values(answers).filter((v) => !!v).length;
  const unansweredCount = examData.questions.length - answeredCount;

  return (
    <div className="space-y-6 pb-16 selection:bg-violet-500 selection:text-white">
      {/* Exam Header Bar */}
      <div className="glass-panel px-6 py-4 rounded-2xl flex items-center justify-between gap-4 border-violet-500/20">
        <div>
          <h1 className="text-base font-extrabold text-white truncate max-w-md">{examData.title}</h1>
          <div className="flex items-center gap-3 text-[11px] text-gray-400 mt-0.5">
            <span>{examData.total_questions} Questions</span>
            <span>•</span>
            <span className={examData.negative_marking ? 'text-amber-400 font-semibold' : ''}>
              {examData.negative_marking ? 'Negative Marking (-0.25)' : 'No Negative Marking'}
            </span>
            <span>•</span>
            <span className="text-emerald-400 font-mono text-[10px]">● {autosaveStatus}</span>
          </div>
        </div>

        {/* Timer & Fullscreen Controls */}
        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border font-mono font-bold text-sm tracking-wider ${
            isTimeCritical
              ? 'bg-red-950/70 border-red-500 text-red-300 animate-pulse'
              : 'bg-violet-950/60 border-violet-500/30 text-cyan-300'
          }`}>
            <Timer className={`w-4 h-4 ${isTimeCritical ? 'text-red-400' : 'text-cyan-400'}`} />
            <span>{formatTimer(secondsRemaining)}</span>
          </div>

          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            title="Toggle Fullscreen"
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Question Arena */}
        <div className="lg:col-span-3 space-y-6">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 min-h-[460px] flex flex-col justify-between">
            {/* Question Header */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-lg bg-violet-600 text-white font-mono font-bold text-xs">
                    Q{currentIdx + 1} of {examData.questions.length}
                  </span>
                  <span className="text-xs px-2.5 py-1 rounded-lg bg-white/5 text-gray-300 capitalize">
                    {currentQ.difficulty} Tier
                  </span>
                  <span className="text-xs px-2.5 py-1 rounded-lg bg-white/5 text-gray-400">
                    +{currentQ.marks} Marks
                  </span>
                </div>

                <button
                  onClick={handleToggleMarkForReview}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold border transition-all ${
                    isMarked
                      ? 'bg-amber-950/60 border-amber-500 text-amber-300'
                      : 'bg-white/5 border-white/10 text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <Bookmark className={`w-3.5 h-3.5 ${isMarked ? 'fill-amber-400 text-amber-400' : ''}`} />
                  <span>{isMarked ? 'Marked for Review' : 'Mark for Review'}</span>
                </button>
              </div>

              {/* Question Text */}
              <h2 className="text-base sm:text-lg font-medium text-white leading-relaxed pt-2">
                {currentQ.question_text}
              </h2>

              {/* Source Verification Badge */}
              {currentQ.source_document_title && (
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-white/5 text-[11px] text-gray-400 border border-white/5">
                  <span className="text-cyan-400 font-medium">Grounded Source:</span>
                  <span>{currentQ.source_document_title}</span>
                  {currentQ.source_page && <span>(Page {currentQ.source_page})</span>}
                </div>
              )}
            </div>

            {/* Answer Options */}
            <div className="space-y-3 pt-4">
              {currentQ.options.map((opt) => {
                const isChosen = selectedOpt === opt.option_key;
                return (
                  <div
                    key={opt.option_key}
                    onClick={() => handleSelectOption(opt.option_key)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-center gap-3.5 ${
                      isChosen
                        ? 'bg-violet-950/70 border-violet-500/80 text-white shadow-md shadow-violet-500/15'
                        : 'bg-white/5 border-white/5 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    <div
                      className={`w-7 h-7 rounded-xl flex items-center justify-center font-bold text-xs shrink-0 ${
                        isChosen ? 'bg-violet-500 text-white' : 'bg-white/10 text-gray-400'
                      }`}
                    >
                      {opt.option_key}
                    </div>
                    <span className="text-xs sm:text-sm leading-relaxed">{opt.option_text}</span>
                  </div>
                );
              })}
            </div>

            {/* Bottom Nav Controls */}
            <div className="pt-6 border-t border-white/5 flex items-center justify-between">
              <button
                disabled={currentIdx === 0}
                onClick={() => setCurrentIdx((prev) => prev - 1)}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 disabled:opacity-30 text-xs font-semibold text-gray-300 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous</span>
              </button>

              <div className="flex items-center gap-3">
                {currentIdx < examData.questions.length - 1 ? (
                  <button
                    onClick={() => setCurrentIdx((prev) => prev + 1)}
                    className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-xs font-semibold text-white shadow-md shadow-violet-500/20 transition-all"
                  >
                    <span>Next Question</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    onClick={() => setShowConfirmModal(true)}
                    className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-xs font-semibold text-white shadow-md shadow-cyan-500/20 transition-all"
                  >
                    <Send className="w-4 h-4" />
                    <span>Review & Final Submit</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Question Palette Sidebar */}
        <div className="space-y-4">
          <div className="glass-panel p-6 rounded-3xl space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-300">Question Palette</h3>

            {/* Status Legend */}
            <div className="grid grid-cols-3 gap-2 text-[10px] text-gray-400 pb-2 border-b border-white/5">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded bg-violet-600" />
                <span>Answered ({answeredCount})</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded bg-amber-500" />
                <span>Review ({reviewMarked.length})</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded bg-white/10" />
                <span>Left ({unansweredCount})</span>
              </div>
            </div>

            {/* Question Buttons Matrix */}
            <div className="grid grid-cols-5 gap-2 pt-1">
              {examData.questions.map((q, idx) => {
                const isCurrent = currentIdx === idx;
                const isAns = !!answers[q.id.toString()];
                const isRev = reviewMarked.includes(q.id);

                let bgClass = 'bg-white/5 text-gray-400 border-white/5';
                if (isRev) {
                  bgClass = 'bg-amber-500/30 text-amber-300 border-amber-500/50';
                } else if (isAns) {
                  bgClass = 'bg-violet-600/80 text-white border-violet-500';
                }

                return (
                  <button
                    key={q.id}
                    onClick={() => setCurrentIdx(idx)}
                    className={`h-9 rounded-xl font-mono text-xs font-bold border transition-all flex items-center justify-center relative ${bgClass} ${
                      isCurrent ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-[#0b0f19]' : ''
                    }`}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>

            {/* Quick Submit Trigger */}
            <div className="pt-4">
              <button
                onClick={() => setShowConfirmModal(true)}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-xs font-bold text-white shadow-md shadow-cyan-500/20 transition-all"
              >
                Submit Exam Now
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Submit Confirmation Dialog Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-white/10 w-full max-w-md rounded-3xl p-6 sm:p-8 space-y-6">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-2xl bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 mx-auto flex items-center justify-center">
                <FileCheck2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white">Submit Examination?</h3>
              <p className="text-xs text-gray-400">
                You will receive your grade, deterministic marks, and 7-step AI feedback coach analysis immediately.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">Answered Questions:</span>
                <span className="font-bold text-emerald-400">{answeredCount} of {examData.total_questions}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Marked for Review:</span>
                <span className="font-bold text-amber-400">{reviewMarked.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Time Left:</span>
                <span className="font-bold text-cyan-400">{formatTimer(secondsRemaining)}</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="w-1/2 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-gray-300 transition-colors"
              >
                Keep Reviewing
              </button>
              <button
                disabled={isSubmitting}
                onClick={handleForceSubmit}
                className="w-1/2 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 disabled:opacity-50 text-xs font-bold text-white shadow-md shadow-violet-500/25 transition-all"
              >
                {isSubmitting ? 'Scoring Answers...' : 'Confirm Submission'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
