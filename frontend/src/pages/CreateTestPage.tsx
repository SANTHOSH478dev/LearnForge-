import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Sparkles,
  Layers,
  Clock,
  ShieldAlert,
  HelpCircle,
  FileText,
  Sliders,
  CheckCircle2,
  ArrowRight,
  BookOpen
} from 'lucide-react';
import { apiFetch } from '../lib/api';
import { DocumentItem, TestDetail } from '../types';

export const CreateTestPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preSelectedDocId = searchParams.get('docId');

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<number[]>([]);
  const [title, setTitle] = useState('');
  const [subject, setSubject] = useState('Computer Science');
  const [questionCount, setQuestionCount] = useState<number>(10);
  const [difficulty, setDifficulty] = useState<string>('medium');
  const [testType, setTestType] = useState<string>('timed_exam');
  const [timeLimit, setTimeLimit] = useState<number>(15);
  const [negativeMarking, setNegativeMarking] = useState<boolean>(false);
  const [questionTypes, setQuestionTypes] = useState<string[]>(['mcq']);
  const [loading, setLoading] = useState(false);
  const [blueprint, setBlueprint] = useState<any | null>(null);
  const [blueprintLoading, setBlueprintLoading] = useState(false);

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const data = await apiFetch<DocumentItem[]>('/documents');
        const completed = data.filter((d) => d.processing_status === 'completed');
        setDocuments(completed);

        if (preSelectedDocId) {
          const matched = completed.find((d) => d.id === parseInt(preSelectedDocId));
          if (matched) {
            setSelectedDocIds([matched.id]);
            setTitle(`Mastery Exam: ${matched.title}`);
          }
        } else if (completed.length > 0) {
          setSelectedDocIds([completed[0].id]);
          setTitle(`Mastery Exam: ${completed[0].title}`);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchDocs();
  }, [preSelectedDocId]);

  const toggleDocSelection = (id: number) => {
    if (selectedDocIds.includes(id)) {
      if (selectedDocIds.length > 1) {
        setSelectedDocIds(selectedDocIds.filter((d) => d !== id));
      }
    } else {
      setSelectedDocIds([...selectedDocIds, id]);
    }
  };

  const handleFetchBlueprint = async () => {
    if (selectedDocIds.length === 0) return;
    setBlueprintLoading(true);
    try {
      const res = await apiFetch('/tests/blueprint', {
        method: 'POST',
        body: JSON.stringify({
          document_ids: selectedDocIds,
          total_questions: questionCount,
          target_difficulty: difficulty,
        }),
      });
      setBlueprint(res);
    } catch (err: any) {
      alert(err.message || 'Blueprint error');
    } finally {
      setBlueprintLoading(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedDocIds.length === 0) {
      alert('Please select at least one study material');
      return;
    }

    setLoading(true);
    try {
      const generatedTest = await apiFetch<TestDetail>('/tests/generate', {
        method: 'POST',
        body: JSON.stringify({
          document_ids: selectedDocIds,
          title: title || 'Assessment Blueprint',
          subject,
          question_count: questionCount,
          difficulty,
          test_type: testType,
          question_types: questionTypes,
          time_limit_minutes: timeLimit,
          negative_marking: negativeMarking,
          negative_mark_value: 0.25,
        }),
      });

      // Jump directly to Exam Arena
      navigate(`/exam/${generatedTest.id}`);
    } catch (err: any) {
      alert(err.message || 'Failed to synthesize questions');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      <div>
        <h1 className="text-2xl font-extrabold text-white">AI Question Generation & Test Config</h1>
        <p className="text-xs text-gray-400 mt-1">
          Configure an assessment strictly grounded in your selected materials.
        </p>
      </div>

      <form onSubmit={handleGenerate} className="space-y-8">
        {/* Step 1: Material Selection */}
        <div className="glass-panel p-6 sm:p-8 rounded-3xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                <span>1. Select Source Material(s)</span>
              </h2>
              <p className="text-xs text-gray-400">Questions are synthesized strictly from these documents</p>
            </div>
            <span className="text-xs text-cyan-400 font-semibold">{selectedDocIds.length} Selected</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            {documents.length === 0 ? (
              <p className="text-xs text-gray-500 py-4 col-span-2">
                No processed documents found. Please upload materials in Document Studio first!
              </p>
            ) : (
              documents.map((doc) => {
                const isSelected = selectedDocIds.includes(doc.id);
                return (
                  <div
                    key={doc.id}
                    onClick={() => toggleDocSelection(doc.id)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-start gap-3 ${
                      isSelected
                        ? 'bg-violet-950/50 border-violet-500/50 text-white shadow-md shadow-violet-500/10'
                        : 'bg-white/5 border-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    <div className={`w-5 h-5 rounded-md flex items-center justify-center shrink-0 mt-0.5 ${
                      isSelected ? 'bg-violet-600 text-white' : 'border border-gray-600'
                    }`}>
                      {isSelected && <CheckCircle2 className="w-4 h-4" />}
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs font-semibold text-gray-200 line-clamp-1">{doc.title}</p>
                      <p className="text-[10px] text-gray-400 uppercase font-mono">{doc.file_type} • {doc.page_count} Pages</p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Step 2: Test Parameters */}
        <div className="glass-panel p-6 sm:p-8 rounded-3xl space-y-6">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-violet-400" />
            <span>2. Assessment Parameters</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1.5">Assessment Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Distributed Systems Midterm Diagnostic"
                className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-xs text-gray-100 focus:outline-none focus:border-violet-500/50"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1.5">Subject Domain</label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-xs text-gray-100 focus:outline-none focus:border-violet-500/50"
              />
            </div>
          </div>

          {/* Question Count & Difficulty */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2">
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-2">Question Count</label>
              <div className="grid grid-cols-4 gap-2">
                {[5, 10, 15, 20].map((num) => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => setQuestionCount(num)}
                    className={`py-2 rounded-xl text-xs font-semibold border transition-all ${
                      questionCount === num
                        ? 'bg-violet-600 border-violet-500 text-white shadow-sm shadow-violet-500/20'
                        : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    {num} Qs
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-300 mb-2">Difficulty Tier</label>
              <div className="grid grid-cols-4 gap-2">
                {['easy', 'medium', 'hard', 'mixed'].map((diff) => (
                  <button
                    key={diff}
                    type="button"
                    onClick={() => setDifficulty(diff)}
                    className={`py-2 rounded-xl text-xs font-semibold capitalize border transition-all ${
                      difficulty === diff
                        ? 'bg-cyan-600 border-cyan-500 text-white shadow-sm shadow-cyan-500/20'
                        : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    {diff}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Test Type & Negative Marking */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2">
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-2">Test Environment</label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'timed_exam', label: 'Timed Exam' },
                  { id: 'practice', label: 'Practice Mode' },
                  { id: 'challenge', label: 'Score Battle' },
                  { id: 'revision', label: 'Adaptive Revision' },
                ].map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setTestType(t.id)}
                    className={`py-2 px-3 rounded-xl text-xs font-medium border text-left transition-all ${
                      testType === t.id
                        ? 'bg-violet-950/60 border-violet-500/40 text-violet-200'
                        : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1.5">
                  Time Limit: <span className="text-cyan-400 font-bold">{timeLimit} Minutes</span>
                </label>
                <input
                  type="range"
                  min={5}
                  max={60}
                  step={5}
                  value={timeLimit}
                  onChange={(e) => setTimeLimit(parseInt(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              {/* Negative marking toggle */}
              <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
                <div className="space-y-0.5">
                  <span className="text-xs font-medium text-gray-200">Negative Marking</span>
                  <p className="text-[10px] text-gray-400">-0.25 marks for wrong answers</p>
                </div>
                <button
                  type="button"
                  onClick={() => setNegativeMarking(!negativeMarking)}
                  className={`w-11 h-6 rounded-full transition-colors relative ${
                    negativeMarking ? 'bg-violet-600' : 'bg-gray-700'
                  }`}
                >
                  <span
                    className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-transform ${
                      negativeMarking ? 'left-6' : 'left-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Blueprint Action Button */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={handleFetchBlueprint}
            disabled={blueprintLoading || selectedDocIds.length === 0}
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 transition-colors"
          >
            <BookOpen className="w-4 h-4" />
            <span>{blueprintLoading ? 'Analyzing Blueprint...' : 'Preview Topic Blueprint'}</span>
          </button>

          <button
            type="submit"
            disabled={loading || selectedDocIds.length === 0}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 disabled:opacity-50 text-white font-bold text-xs shadow-lg shadow-violet-500/25 flex items-center gap-2 transition-all group"
          >
            <Sparkles className="w-4 h-4 text-cyan-200 group-hover:rotate-12 transition-transform" />
            <span>{loading ? 'Synthesizing Grounded Exam...' : 'Generate & Enter Exam Arena'}</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>

        {/* Blueprint Drawer Preview */}
        {blueprint && (
          <div className="glass-panel p-6 rounded-2xl border-cyan-500/30 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>{blueprint.title}</span>
            </h3>
            <p className="text-xs text-gray-300">{blueprint.summary}</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              {blueprint.topics.map((t: any, i: number) => (
                <div key={i} className="p-3 rounded-xl bg-white/5 border border-white/5 flex justify-between items-center">
                  <span className="text-xs font-semibold text-gray-200">{t.topic}</span>
                  <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded">
                    {t.question_allocation} Qs
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </form>
    </div>
  );
};
