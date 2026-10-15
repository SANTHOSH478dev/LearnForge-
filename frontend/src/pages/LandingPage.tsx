import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  UploadCloud,
  Cpu,
  Timer,
  BarChart3,
  Brain,
  ShieldCheck,
  CheckCircle2,
  FileText
} from 'lucide-react';
import { LearnForgeLogo } from '../components/logo/LearnForgeLogo';
import { useAuth } from '../context/AuthContext';
import { apiFetch, setStoredToken } from '../lib/api';
import { AuthResponse } from '../types';

export const LandingPage: React.FC = () => {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();

  const handleDemoLogin = async () => {
    try {
      const data = await apiFetch<AuthResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: 'student@learnforge.ai',
          password: 'password123',
        }),
      });
      login(data.access_token, {
        id: data.user_id,
        email: data.email,
        full_name: data.full_name,
        role: data.role,
        is_active: true,
      });
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
      navigate('/login');
    }
  };

  const steps = [
    { title: 'Upload Material', desc: 'Drop PDFs, DOCX, PPTX slides, or lecture notes. Text is extracted and chunked.', icon: UploadCloud },
    { title: 'AI Generation', desc: 'Calibrated questions synthesized strictly from verified citations and concepts.', icon: Cpu },
    { title: 'Timed Exam Arena', desc: 'Simulate realistic exam conditions with server-enforced countdown deadlines.', icon: Timer },
    { title: '7-Step AI Coach', desc: 'Discover why mistakes happened with concrete examples, concepts, and revision steps.', icon: Brain },
    { title: 'Forge Weaknesses', desc: 'Adaptive revision paths, spaced-repetition flashcards, and targeted retakes.', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-100 flex flex-col selection:bg-violet-500 selection:text-white">
      {/* Navigation Bar */}
      <header className="border-b border-white/5 bg-[#0b0f19]/70 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <LearnForgeLogo size="md" showTagline={true} />
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium text-xs shadow-md shadow-violet-500/20 transition-all"
              >
                <span>Enter Dashboard</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            ) : (
              <>
                <button
                  onClick={handleDemoLogin}
                  className="px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-gray-300 font-medium transition-colors"
                >
                  ⚡ Quick Demo Login
                </button>
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs text-gray-200 font-medium transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium text-xs shadow-md shadow-violet-500/20 transition-all"
                >
                  <span>Get Started</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-28 px-6 overflow-hidden">
        {/* Glow ambient background elements */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-violet-600/20 via-indigo-600/15 to-cyan-500/20 blur-[120px] rounded-full pointer-events-none" />

        <div className="max-w-5xl mx-auto text-center relative z-10 space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-950/70 border border-violet-500/30 text-violet-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Intelligent Student Learning & Assessment Platform</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Turn Every Page <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-indigo-300 to-cyan-400">
              Into Measurable Progress.
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-gray-400 leading-relaxed">
            Upload your course materials and automatically generate syllabus-grounded quizzes,
            timed exams with deterministic scoring, 7-step cognitive feedback, and adaptive weakness revision.
          </p>

          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={handleDemoLogin}
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-semibold text-sm shadow-lg shadow-violet-600/30 flex items-center justify-center gap-2 transition-all group"
            >
              <span>Explore Demo Student Account</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <Link
              to="/register"
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 font-semibold text-sm flex items-center justify-center transition-colors"
            >
              Create Free Account
            </Link>
          </div>

          <div className="pt-8 flex items-center justify-center gap-6 text-xs text-gray-500">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Grounded in Your Own Notes</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Deterministic Server-Side Scoring</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Exportable PDF Reports</span>
            </div>
          </div>
        </div>
      </section>

      {/* The 5-Step Workflow Progression */}
      <section className="py-16 px-6 bg-[#111827]/40 border-y border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12 space-y-2">
            <h2 className="text-2xl font-bold text-white">The Continuous Learning Cycle</h2>
            <p className="text-xs text-gray-400">From raw course material to verified mastery in 5 calibrated steps</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {steps.map((s, idx) => {
              const Icon = s.icon;
              return (
                <div
                  key={s.title}
                  className="glass-card p-5 rounded-2xl flex flex-col justify-between space-y-4 hover:border-violet-500/30 transition-all group"
                >
                  <div className="flex items-center justify-between">
                    <div className="w-10 h-10 rounded-xl bg-violet-950/60 border border-violet-500/20 flex items-center justify-center text-violet-400 group-hover:text-cyan-300 transition-colors">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-xs font-mono font-bold text-gray-500">0{idx + 1}</span>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-200 mb-1">{s.title}</h3>
                    <p className="text-xs text-gray-400 leading-relaxed">{s.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Core Feature Deep-Dives */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <h2 className="text-3xl font-extrabold text-white">Built for True Exam Readiness</h2>
            <p className="text-sm text-gray-400">
              Unlike generic flashcard apps, LearnForge AI replicates actual examination mechanics with strict source citations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-panel p-6 rounded-2xl space-y-4">
              <div className="w-10 h-10 rounded-xl bg-cyan-950/60 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-white">Exam Arena & Anti-Cheat Sync</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                Server-side deadline computation ensures tests cannot be submitted past the official time limit. Answers autosave in the background so accidental refreshes never lose progress.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-2xl space-y-4">
              <div className="w-10 h-10 rounded-xl bg-violet-950/60 border border-violet-500/30 flex items-center justify-center text-violet-400">
                <Brain className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-white">"Forge My Weaknesses"</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                Automatically identifies topics where your accuracy dipped below passing thresholds and builds a 1-click targeted practice exam to bridge the knowledge gap.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-2xl space-y-4">
              <div className="w-10 h-10 rounded-xl bg-amber-950/60 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-white">Downloadable Assessment Reports</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                Export complete PDF assessment scorecards complete with topic breakdowns, time analytics, and personalized AI Coach insights.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-white/5 py-8 px-6 bg-[#0b0f19]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <LearnForgeLogo size="sm" showTagline={false} />
            <span>© 2026 LearnForge AI. All rights reserved.</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login" className="hover:text-gray-300 transition-colors">Sign In</Link>
            <Link to="/register" className="hover:text-gray-300 transition-colors">Register</Link>
            <span className="text-zinc-600">|</span>
            <span className="text-cyan-400 font-mono">Turn Every Page Into Progress</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
