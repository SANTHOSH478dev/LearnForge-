import React, { useState, useEffect } from 'react';
import {
  User,
  GraduationCap,
  Award,
  Sparkles,
  BookOpen,
  Target,
  Flame,
  CheckCircle2,
  FileText,
  Clock
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState<any | null>(null);
  const [achievements, setAchievements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const dash = await apiFetch<any>('/dashboard');
        setProfileData(dash);

        // Pre-seeded badges
        setAchievements([
          {
            badge_title: 'Cadet of Knowledge',
            badge_description: 'Activated LearnForge AI and initialized personalized learning workspace.',
            icon: Sparkles,
            color: 'text-violet-400',
            bg: 'bg-violet-950/60 border-violet-500/30',
          },
          {
            badge_title: 'Knowledge Ingestion',
            badge_description: 'Uploaded and successfully chunked academic source documents.',
            icon: FileText,
            color: 'text-cyan-400',
            bg: 'bg-cyan-950/60 border-cyan-500/30',
          },
          {
            badge_title: 'Exam Pioneer',
            badge_description: 'Completed first timed assessment under server-side deadline monitoring.',
            icon: Clock,
            color: 'text-amber-400',
            bg: 'bg-amber-950/60 border-amber-500/30',
          },
        ]);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16 selection:bg-violet-500 selection:text-white">
      {/* Top Banner */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden flex flex-col sm:flex-row items-center gap-6 border-violet-500/20">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-violet-600 to-cyan-500 flex items-center justify-center font-bold text-2xl text-white shadow-xl shadow-violet-500/20 shrink-0">
          {user?.full_name ? user.full_name[0].toUpperCase() : 'S'}
        </div>

        <div className="space-y-1 text-center sm:text-left flex-1">
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <h1 className="text-2xl font-extrabold text-white">{user?.full_name || 'Student'}</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-violet-950 text-violet-300 border border-violet-500/30 uppercase">
              {user?.role || 'student'}
            </span>
          </div>
          <p className="text-xs text-gray-400">{user?.email}</p>
          <p className="text-xs text-cyan-300 font-medium pt-1">
            Senior Undergraduate • Computer Science & Engineering
          </p>
        </div>

        <div className="flex items-center gap-4 text-center shrink-0">
          <div className="px-4 py-2 rounded-2xl bg-white/5 border border-white/5">
            <span className="text-xs text-gray-400">Streak</span>
            <p className="text-lg font-bold text-amber-400 flex items-center justify-center gap-1">
              <Flame className="w-4 h-4" />
              <span>{profileData?.current_streak_days || 5}d</span>
            </p>
          </div>
          <div className="px-4 py-2 rounded-2xl bg-white/5 border border-white/5">
            <span className="text-xs text-gray-400">Exams</span>
            <p className="text-lg font-bold text-white">{profileData?.total_tests_completed || 1}</p>
          </div>
        </div>
      </div>

      {/* Profile Details & Academic Goals */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-violet-400" />
            <span>Academic Profile</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-white/5 space-y-1">
              <span className="text-gray-400 text-[11px] font-medium">Academic Level</span>
              <p className="font-semibold text-gray-200">Senior Undergraduate (Final Year)</p>
            </div>

            <div className="p-3 rounded-xl bg-white/5 space-y-1">
              <span className="text-gray-400 text-[11px] font-medium">Target Subjects</span>
              <p className="font-semibold text-gray-200">Distributed Systems, Data Structures & Algorithms</p>
            </div>

            <div className="p-3 rounded-xl bg-white/5 space-y-1">
              <span className="text-gray-400 text-[11px] font-medium">Daily Target</span>
              <p className="font-semibold text-gray-200">45 Minutes Active Exam & Revision</p>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Target className="w-4 h-4 text-cyan-400" />
            <span>Learning Objectives</span>
          </h3>

          <div className="p-4 rounded-2xl bg-white/5 border border-white/5 space-y-3">
            <p className="text-xs text-gray-300 leading-relaxed">
              "Prepare for placement examinations, master collegiate syllabus topics with high confidence, and maintain an S-Grade assessment standard."
            </p>
            <div className="flex items-center gap-2 text-[11px] text-emerald-400 font-semibold">
              <CheckCircle2 className="w-4 h-4" />
              <span>Syllabus Verification Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Unlocked Milestones & Achievements */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-400" />
            <span>Unlocked Progress Milestones</span>
          </h3>
          <span className="text-xs text-gray-400">{achievements.length} Badges Earned</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {achievements.map((ach, idx) => {
            const Icon = ach.icon;
            return (
              <div
                key={idx}
                className={`p-5 rounded-2xl border ${ach.bg} space-y-3 flex flex-col justify-between`}
              >
                <div className="flex items-center justify-between">
                  <div className={`w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center ${ach.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-mono text-gray-400 font-semibold uppercase">Verified</span>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white mb-1">{ach.badge_title}</h4>
                  <p className="text-[11px] text-gray-400 leading-relaxed">{ach.badge_description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
