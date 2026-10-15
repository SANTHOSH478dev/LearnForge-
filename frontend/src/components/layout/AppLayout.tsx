import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  PlusCircle,
  Brain,
  HelpCircle,
  User,
  LogOut,
  Menu,
  X,
  Search,
  Bell,
  Sparkles,
  ChevronRight,
  Flame,
  Award
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { LearnForgeLogo } from '../logo/LearnForgeLogo';

export const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Document Studio', path: '/documents', icon: FileText },
    { name: 'Create Test', path: '/tests/create', icon: PlusCircle },
    { name: 'Revision Hub', path: '/revision', icon: Brain },
    { name: 'Doubt Solver', path: '/doubts', icon: HelpCircle },
    { name: 'Profile & Badges', path: '/profile', icon: User },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-100 flex flex-col md:flex-row">
      {/* Mobile Top Header */}
      <div className="md:hidden flex items-center justify-between px-4 py-3 bg-[#111827]/90 backdrop-blur-md border-b border-white/10 sticky top-0 z-50">
        <LearnForgeLogo size="sm" showTagline={false} />
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300"
        >
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <aside
        className={`fixed md:sticky top-0 h-screen w-64 bg-[#111827]/95 md:bg-[#111827]/80 backdrop-blur-xl border-r border-white/10 flex flex-col justify-between z-40 transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div>
          {/* Logo Branding */}
          <div className="px-6 py-6 border-b border-white/5">
            <LearnForgeLogo size="md" showTagline={true} />
          </div>

          {/* Navigation Items */}
          <nav className="px-3 py-6 space-y-1.5">
            <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-gray-500">
              Workspace
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-violet-600/25 to-indigo-600/15 text-white border border-violet-500/30 shadow-sm shadow-violet-500/10'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-violet-400' : 'text-gray-400'}`} />
                  <span>{item.name}</span>
                  {isActive && <ChevronRight className="w-3.5 h-3.5 ml-auto text-violet-400" />}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Quick Revision Card & User Profile Footer */}
        <div className="p-4 border-t border-white/10 space-y-3">
          {/* Adaptive Forge Banner */}
          <div
            onClick={() => {
              setSidebarOpen(false);
              navigate('/revision');
            }}
            className="p-3 rounded-xl bg-gradient-to-br from-violet-950/60 to-indigo-950/40 border border-violet-500/20 cursor-pointer hover:border-violet-500/40 transition-all group"
          >
            <div className="flex items-center gap-2 text-xs font-semibold text-violet-300">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400 group-hover:rotate-12 transition-transform" />
              <span>Forge Weaknesses</span>
            </div>
            <p className="text-[11px] text-gray-400 mt-1">
              1-click targeted practice from past exam mistakes.
            </p>
          </div>

          {/* User Profile Info */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-violet-600 to-cyan-500 flex items-center justify-center font-bold text-xs text-white shrink-0">
                {user?.full_name ? user.full_name[0].toUpperCase() : 'S'}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-medium text-gray-200 truncate">{user?.full_name || 'Student'}</p>
                <p className="text-[10px] text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              title="Logout"
              className="p-1.5 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-950/30 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="hidden md:flex items-center justify-between px-8 py-3.5 bg-[#111827]/40 backdrop-blur-md border-b border-white/5 sticky top-0 z-30">
          {/* Search bar */}
          <div className="relative w-80">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search documents, topics, questions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 bg-white/5 border border-white/10 rounded-xl text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/30 transition-all"
            />
          </div>

          {/* Right Header Actions */}
          <div className="flex items-center gap-4">
            {/* Streak Indicator */}
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold">
              <Flame className="w-4 h-4 text-amber-400 animate-pulse" />
              <span>5-Day Streak</span>
            </div>

            {/* Quick Create Test Button */}
            <button
              onClick={() => navigate('/tests/create')}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white text-xs font-medium shadow-md shadow-violet-500/20 transition-all"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>New Exam</span>
            </button>

            {/* Notifications */}
            <button className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors relative">
              <Bell className="w-4 h-4" />
              <span className="w-2 h-2 rounded-full bg-cyan-400 absolute top-1.5 right-1.5" />
            </button>
          </div>
        </header>

        {/* Page Content Body */}
        <main className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
