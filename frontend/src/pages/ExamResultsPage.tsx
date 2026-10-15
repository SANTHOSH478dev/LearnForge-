import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Award,
  CheckCircle2,
  XCircle,
  Clock,
  Download,
  Brain,
  Sparkles,
  ArrowRight,
  TrendingUp,
  RotateCcw,
  BookOpen,
  ChevronDown,
  ChevronUp,
  FileText
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { apiFetch, downloadReportPdf } from '../lib/api';
import { AttemptResultData } from '../types';

export const ExamResultsPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [results, setResults] = useState<AttemptResultData | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [expandedMistakes, setExpandedMistakes] = useState<Record<number, boolean>>({});

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await apiFetch<AttemptResultData>(`/attempts/${attemptId}/results`);
        setResults(data);
        // Expand first mistake automatically
        const firstWrong = data.question_results.find((q) => !q.is_correct);
        if (firstWrong) {
          setExpandedMistakes({ [firstWrong.question_id]: true });
        }
      } catch (err: any) {
        alert(err.message || 'Could not load exam results');
        navigate('/dashboard');
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [attemptId, navigate]);

  const handleDownloadPdf = async () => {
    if (!results) return;
    setDownloadingPdf(true);
    try {
      await downloadReportPdf(results.attempt_id);
    } catch (err: any) {
      alert(err.message || 'Could not generate PDF report');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const toggleMistakeExpand = (qid: number) => {
    setExpandedMistakes((prev) => ({ ...prev, [qid]: !prev[qid] }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-violet-500 mx-auto" />
          <p className="text-xs text-gray-400">Compiling official scorecard and AI feedback coach analysis...</p>
        </div>
      </div>
    );
  }

  if (!results) return null;

  const gradeColors: Record<string, string> = {
    S: 'from-emerald-500 to-teal-400 text-emerald-300 border-emerald-500/30',
    A: 'from-emerald-500 to-cyan-400 text-emerald-300 border-emerald-500/30',
    B: 'from-violet-500 to-indigo-400 text-violet-300 border-violet-500/30',
    C: 'from-amber-500 to-orange-400 text-amber-300 border-amber-500/30',
    D: 'from-amber-600 to-red-400 text-amber-400 border-amber-500/30',
    F: 'from-red-600 to-rose-400 text-red-400 border-red-500/30',
  };

  const activeGradeStyle = gradeColors[results.grade] || gradeColors.B;

  return (
    <div className="space-y-8 pb-16 selection:bg-violet-500 selection:text-white">
      {/* Top Banner Scorecard */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6 border-violet-500/20">
        <div className="space-y-3 relative z-10">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">Official Exam Scorecard</span>
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            <span className="text-xs text-gray-400">Server Verified</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">{results.test_title}</h1>

          <div className="flex flex-wrap items-center gap-4 text-xs text-gray-300">
            <span className="flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-cyan-400" />
              <span>Time: {Math.floor(results.time_taken_seconds / 60)}m {results.time_taken_seconds % 60}s</span>
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Correct: {results.correct_count}</span>
            </span>
            <span className="flex items-center gap-1.5">
              <XCircle className="w-4 h-4 text-rose-400" />
              <span>Incorrect: {results.incorrect_count}</span>
            </span>
          </div>

          {/* Previous Attempt Improvement Badge */}
          {results.comparison_with_previous.has_previous && (
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>{results.comparison_with_previous.message}</span>
            </div>
          )}
        </div>

        {/* Grade Badge */}
        <div className="flex items-center gap-6 relative z-10 shrink-0">
          <div className={`w-28 h-28 rounded-3xl bg-gradient-to-br ${activeGradeStyle} p-0.5 shadow-xl flex items-center justify-center`}>
            <div className="w-full h-full bg-[#111827] rounded-[22px] flex flex-col items-center justify-center">
              <span className="text-3xl font-black text-white">{results.grade}</span>
              <span className="text-xs font-mono font-semibold text-gray-400">{results.percentage}%</span>
            </div>
          </div>

          <div className="space-y-2">
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/40 text-xs font-semibold text-cyan-300 transition-all shadow-sm"
            >
              <Download className="w-4 h-4" />
              <span>{downloadingPdf ? 'Generating PDF...' : 'Download PDF Report'}</span>
            </button>

            <button
              onClick={() => navigate('/revision')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-violet-500/20 transition-all"
            >
              <Sparkles className="w-4 h-4 text-cyan-300" />
              <span>Forge Weaknesses in Hub</span>
            </button>
          </div>
        </div>
      </div>

      {/* AI Qualitative Feedback & Topic Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Qualitative Coach Review */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Brain className="w-4 h-4 text-violet-400" />
            <span>AI Feedback Coach Insights</span>
          </h3>

          <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
            <p className="text-xs text-gray-300 leading-relaxed">
              {results.ai_summary_feedback || 'Solid conceptual performance with opportunities for targeted review.'}
            </p>
          </div>

          <div className="space-y-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-cyan-400">Recommended Study Plan</span>
            <p className="text-xs text-gray-300 bg-cyan-950/20 border border-cyan-500/20 p-3 rounded-xl leading-relaxed">
              {results.ai_study_plan_recommendation || 'Review key definitions and run a 5-question adaptive review set.'}
            </p>
          </div>
        </div>

        {/* Topic Breakdown Bar Chart */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-cyan-400" />
            <span>Topic-Wise Accuracy Breakdown</span>
          </h3>

          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={results.topic_breakdown}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="topic" stroke="#9ca3af" fontSize={10} tickLine={false} />
                <YAxis stroke="#9ca3af" fontSize={10} domain={[0, 100]} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  itemStyle={{ color: '#06b6d4', fontSize: '11px' }}
                />
                <Bar dataKey="accuracy" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Question Results & 7-Step AI Feedback Coach */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-violet-400" />
            <span>Detailed Question Review & 7-Step Cognitive Feedback</span>
          </h2>
          <span className="text-xs text-gray-400">Click any card to inspect full AI analysis</span>
        </div>

        <div className="space-y-4">
          {results.question_results.map((qr, idx) => {
            const isExpanded = !!expandedMistakes[qr.question_id];
            const isCorrect = qr.is_correct;
            const fb = qr.ai_feedback;

            return (
              <div
                key={qr.question_id}
                className={`glass-panel rounded-2xl border transition-all ${
                  isCorrect ? 'border-emerald-500/20' : 'border-rose-500/30'
                }`}
              >
                {/* Header row */}
                <div
                  onClick={() => toggleMistakeExpand(qr.question_id)}
                  className="p-5 flex items-center justify-between cursor-pointer hover:bg-white/5 transition-colors rounded-2xl"
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                      isCorrect ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' : 'bg-rose-950 text-rose-400 border border-rose-500/30'
                    }`}>
                      {idx + 1}
                    </span>
                    <div>
                      <p className="text-xs font-semibold text-white line-clamp-1">{qr.question_text}</p>
                      <p className="text-[11px] text-gray-400 font-mono mt-0.5">
                        Topic: {qr.topic_tag} • Marks: {qr.marks_awarded} / {qr.marks_possible}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className={`px-2.5 py-1 rounded text-[11px] font-bold ${
                      isCorrect ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                    }`}>
                      {isCorrect ? 'CORRECT' : (qr.is_unanswered ? 'SKIPPED' : 'INCORRECT')}
                    </span>
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                  </div>
                </div>

                {/* Expanded Details & 7-Step Reasoning */}
                {isExpanded && (
                  <div className="px-6 pb-6 pt-2 border-t border-white/5 space-y-4">
                    {/* User answer vs Correct answer */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                      <div className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400">Your Selection:</span>
                        <p className={`font-semibold ${isCorrect ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {qr.user_answer ? `Option ${qr.user_answer}` : 'Left Unanswered'}
                        </p>
                      </div>
                      <div className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400">Official Correct Answer:</span>
                        <p className="font-semibold text-emerald-400">{qr.correct_answer}</p>
                      </div>
                    </div>

                    {/* Grounded Citation */}
                    {qr.source_citation?.document_title && (
                      <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/20 text-xs space-y-1">
                        <span className="font-semibold text-cyan-300">Grounded Citation:</span>
                        <p className="text-gray-300">
                          {qr.source_citation.document_title} (Page {qr.source_citation.page_number || 1})
                        </p>
                        {qr.source_citation.snippet && (
                          <p className="text-[11px] text-gray-400 italic">"{qr.source_citation.snippet}"</p>
                        )}
                      </div>
                    )}

                    {/* 7-Step AI Feedback Coach (for mistakes) */}
                    {fb && (
                      <div className="p-4 rounded-xl bg-violet-950/30 border border-violet-500/30 space-y-3">
                        <div className="flex items-center gap-2 text-violet-300 text-xs font-bold uppercase tracking-wider">
                          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                          <span>7-Step Cognitive Feedback Coach</span>
                        </div>

                        <div className="space-y-2 text-xs">
                          <div>
                            <span className="font-semibold text-rose-300">Why Selected Answer Was Incorrect:</span>
                            <p className="text-gray-300 mt-0.5">{fb.why_selected_incorrect}</p>
                          </div>
                          <div>
                            <span className="font-semibold text-violet-300">Underlying Concept:</span>
                            <p className="text-gray-300 mt-0.5">{fb.underlying_concept}</p>
                          </div>
                          <div>
                            <span className="font-semibold text-cyan-300">Simple Analogy / Real-World Example:</span>
                            <p className="text-gray-300 mt-0.5">{fb.simple_example}</p>
                          </div>
                          <div>
                            <span className="font-semibold text-amber-300">Document Section to Revise:</span>
                            <p className="text-gray-300 mt-0.5">{fb.document_section_to_revise}</p>
                          </div>
                          <div>
                            <span className="font-semibold text-emerald-300">Follow-up Challenge Question:</span>
                            <p className="text-gray-300 mt-0.5 italic">{fb.follow_up_question}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {!fb && qr.explanation && (
                      <div className="p-3 rounded-xl bg-white/5 text-xs text-gray-300">
                        <span className="font-semibold text-cyan-300">Explanation: </span>
                        {qr.explanation}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
