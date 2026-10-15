import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  CheckCircle,
  Clock,
  TrendingUp,
  Award,
  Sparkles,
  ArrowRight,
  Flame,
  Target,
  AlertTriangle,
  PlayCircle,
  Plus
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';
import { DashboardMetrics } from '../types';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const data = await apiFetch<DashboardMetrics>('/dashboard');
        setMetrics(data);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-violet-500" />
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-center py-20 text-gray-400">
        Failed to load dashboard data. Please try refreshing.
      </div>
    );
  }

  const statCards = [
    { label: 'Study Materials', value: metrics.total_materials_uploaded, icon: FileText, color: 'text-cyan-400', bg: 'bg-cyan-950/40 border-cyan-500/20' },
    { label: 'Exams Completed', value: metrics.total_tests_completed, icon: CheckCircle, color: 'text-violet-400', bg: 'bg-violet-950/40 border-violet-500/20' },
    { label: 'Average Score', value: `${metrics.average_score_percentage}%`, icon: TrendingUp, color: 'text-emerald-400', bg: 'bg-emerald-950/40 border-emerald-500/20' },
    { label: 'Study Time', value: `${metrics.study_time_minutes}m`, icon: Clock, color: 'text-amber-400', bg: 'bg-amber-950/40 border-amber-500/20' },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Welcome Banner */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6 border-violet-500/20">
        <div className="absolute right-0 top-0 w-96 h-96 bg-gradient-to-bl from-violet-600/15 via-cyan-500/10 to-transparent blur-3xl pointer-events-none" />

        <div className="space-y-2 relative z-10">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">Student Workspace</span>
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            <span className="text-xs text-gray-400">Term 2026</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Welcome back, {user?.full_name?.split(' ')[0] || 'Scholar'}!
          </h1>
          <p className="text-xs sm:text-sm text-gray-400 max-w-xl">
            You are on a <span className="text-amber-400 font-semibold">{metrics.current_streak_days}-day study streak</span>.
            Target today: {metrics.daily_goal_minutes} minutes of active problem solving.
          </p>

          {/* Daily Goal Bar */}
          <div className="pt-2 max-w-md space-y-1.5">
            <div className="flex justify-between text-[11px] text-gray-400 font-medium">
              <span>Daily Goal Progress</span>
              <span className="text-violet-300 font-semibold">{metrics.daily_goal_progress_percent}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-white/10 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-violet-500 to-cyan-400 transition-all duration-500"
                style={{ width: `${metrics.daily_goal_progress_percent}%` }}
              />
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 relative z-10 shrink-0">
          <button
            onClick={() => navigate('/documents')}
            className="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-gray-200 flex items-center justify-center gap-2 transition-colors"
          >
            <Plus className="w-4 h-4 text-cyan-400" />
            <span>Upload Material</span>
          </button>
          <button
            onClick={() => navigate('/tests/create')}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-violet-500/25 flex items-center justify-center gap-2 transition-all"
          >
            <Sparkles className="w-4 h-4 text-cyan-300" />
            <span>Create AI Test</span>
          </button>
        </div>
      </div>

      {/* 4 Top KPI Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map((c) => {
          const Icon = c.icon;
          return (
            <div key={c.label} className={`p-5 rounded-2xl border ${c.bg} backdrop-blur-md space-y-2`}>
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">{c.label}</span>
                <Icon className={`w-4 h-4 ${c.color}`} />
              </div>
              <p className="text-2xl font-bold text-white tracking-tight">{c.value}</p>
            </div>
          );
        })}
      </div>

      {/* Recommended Next Step & Daily Challenge */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Next Step Card */}
        <div className="md:col-span-2 glass-panel p-6 rounded-2xl border-cyan-500/20 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-cyan-400">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Recommended Next Step</span>
            </div>
            <h3 className="text-lg font-bold text-white">{metrics.recommended_next_step.title}</h3>
            <p className="text-xs text-gray-400 leading-relaxed">{metrics.recommended_next_step.description}</p>
          </div>
          <div>
            <button
              onClick={() => navigate(metrics.recommended_next_step.action_route)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-xs font-semibold text-cyan-300 transition-colors"
            >
              <span>{metrics.recommended_next_step.action_text}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Daily Challenge */}
        <div className="glass-panel p-6 rounded-2xl border-amber-500/20 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
                <Flame className="w-3.5 h-3.5" />
                <span>Daily Challenge</span>
              </span>
              <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-500/20 text-amber-300">
                {metrics.daily_challenge.reward_points}
              </span>
            </div>
            <h4 className="text-sm font-bold text-white">{metrics.daily_challenge.title}</h4>
            <p className="text-xs text-gray-400">{metrics.daily_challenge.objective}</p>
          </div>

          <div className="pt-2">
            {metrics.daily_challenge.is_completed ? (
              <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                <CheckCircle className="w-4 h-4" /> Challenge Completed!
              </span>
            ) : (
              <button
                onClick={() => navigate('/tests/create')}
                className="w-full py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-xs font-semibold text-amber-300 transition-colors"
              >
                Start Challenge Exam
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Analytics Row: Weekly Performance & Subject Accuracy */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Weekly Chart */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-violet-400" />
              <span>Weekly Score Performance</span>
            </h3>
            <span className="text-xs text-gray-500">Past 7 Days</span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.weekly_performance}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="day" stroke="#9ca3af" fontSize={11} tickLine={false} />
                <YAxis stroke="#9ca3af" fontSize={11} domain={[0, 100]} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  itemStyle={{ color: '#8b5cf6', fontSize: '12px' }}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#8b5cf6"
                  strokeWidth={3}
                  dot={{ fill: '#06b6d4', r: 4 }}
                  activeDot={{ r: 6, fill: '#22d3ee' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Subject Accuracy Bar Chart */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Target className="w-4 h-4 text-cyan-400" />
              <span>Subject-Wise Accuracy</span>
            </h3>
            <span className="text-xs text-gray-500">Mastery Levels</span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.subject_accuracy}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="subject" stroke="#9ca3af" fontSize={11} tickLine={false} />
                <YAxis stroke="#9ca3af" fontSize={11} domain={[0, 100]} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  itemStyle={{ color: '#06b6d4', fontSize: '12px' }}
                />
                <Bar dataKey="accuracy" fill="#06b6d4" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Weakest Concepts & Recent Attempts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Weakest Concepts with 1-Click Forge */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Weakest Concepts Identified</span>
            </h3>
            <button
              onClick={() => navigate('/revision')}
              className="text-xs font-semibold text-violet-400 hover:text-violet-300 transition-colors"
            >
              Forge in Hub →
            </button>
          </div>

          <div className="space-y-3">
            {metrics.weakest_concepts.length === 0 ? (
              <p className="text-xs text-gray-400 py-4">No weak concepts logged yet! Take exams to calibrate.</p>
            ) : (
              metrics.weakest_concepts.map((w) => (
                <div key={w.topic} className="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-gray-200">{w.topic}</p>
                    <p className="text-[11px] text-gray-400">{w.attempts} questions answered</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-red-400">{w.accuracy}%</span>
                    <p className="text-[10px] text-gray-500">Accuracy</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Attempts */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Award className="w-4 h-4 text-emerald-400" />
              <span>Recent Test Attempts</span>
            </h3>
            <span className="text-xs text-gray-500">Graded Records</span>
          </div>

          <div className="space-y-3">
            {metrics.recent_attempts.length === 0 ? (
              <p className="text-xs text-gray-400 py-4">No completed tests yet. Start your first exam above!</p>
            ) : (
              metrics.recent_attempts.map((a) => (
                <div
                  key={a.id}
                  onClick={() => navigate(`/attempts/${a.id}/results`)}
                  className="p-3 rounded-xl bg-white/5 border border-white/5 hover:border-violet-500/30 cursor-pointer flex items-center justify-between transition-all"
                >
                  <div className="space-y-0.5">
                    <p className="text-xs font-semibold text-gray-200">{a.title}</p>
                    <p className="text-[10px] text-gray-500">{a.date}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold text-gray-200">{a.percentage}%</span>
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      ['S', 'A'].includes(a.grade) ? 'bg-emerald-500/20 text-emerald-300' : (['B', 'C'].includes(a.grade) ? 'bg-amber-500/20 text-amber-300' : 'bg-red-500/20 text-red-300')
                    }`}>
                      Grade {a.grade}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
