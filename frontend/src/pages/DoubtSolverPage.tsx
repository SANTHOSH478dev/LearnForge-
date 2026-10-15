import React, { useState, useEffect } from 'react';
import {
  HelpCircle,
  Send,
  Sparkles,
  BookOpen,
  FileText,
  User,
  Bot,
  CornerDownRight,
  ChevronRight
} from 'lucide-react';
import { apiFetch } from '../lib/api';
import { DoubtMessage, DocumentItem } from '../types';

export const DoubtSolverPage: React.FC = () => {
  const [messages, setMessages] = useState<DoubtMessage[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const init = async () => {
      try {
        const [docs, history] = await Promise.all([
          apiFetch<DocumentItem[]>('/documents'),
          apiFetch<DoubtMessage[]>('/doubts'),
        ]);
        setDocuments(docs.filter((d) => d.processing_status === 'completed'));
        setMessages(history.reverse());
      } catch (err) {
        console.error(err);
      }
    };
    init();
  }, []);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const currentQuery = query.trim();
    setQuery('');
    setLoading(true);

    try {
      const res = await apiFetch<DoubtMessage>('/doubts/ask', {
        method: 'POST',
        body: JSON.stringify({
          query: currentQuery,
          document_id: selectedDocId,
        }),
      });
      setMessages((prev) => [...prev, res]);
    } catch (err: any) {
      alert(err.message || 'Doubt solver error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16 selection:bg-violet-500 selection:text-white">
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-3xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-violet-500/20">
        <div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-white flex items-center gap-2">
            <HelpCircle className="w-6 h-6 text-cyan-400" />
            <span>AI Doubt Solver</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Ask any question about your notes. Answers are strictly grounded with citations to pages and sections.
          </p>
        </div>

        {/* Filter by document */}
        <select
          value={selectedDocId || ''}
          onChange={(e) => setSelectedDocId(e.target.value ? parseInt(e.target.value) : null)}
          className="px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-gray-200 focus:outline-none focus:border-violet-500/50"
        >
          <option value="" className="bg-[#111827]">All Uploaded Materials</option>
          {documents.map((d) => (
            <option key={d.id} value={d.id} className="bg-[#111827]">
              {d.title}
            </option>
          ))}
        </select>
      </div>

      {/* Chat Messages Log */}
      <div className="glass-panel p-6 rounded-3xl min-h-[440px] flex flex-col justify-between space-y-6">
        <div className="space-y-6 overflow-y-auto max-h-[550px] pr-2">
          {messages.length === 0 ? (
            <div className="text-center py-16 space-y-2">
              <Sparkles className="w-8 h-8 text-violet-400 mx-auto" />
              <h3 className="text-sm font-semibold text-white">Ask your first question</h3>
              <p className="text-xs text-gray-500 max-w-sm mx-auto">
                E.g. "What ensures two leaders aren't elected in the same term in Raft?" or "What is AVL balance factor?"
              </p>
            </div>
          ) : (
            messages.map((m) => (
              <div key={m.id} className="space-y-4">
                {/* User Prompt */}
                <div className="flex items-start gap-3 justify-end">
                  <div className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white p-3.5 rounded-2xl rounded-tr-sm max-w-lg text-xs leading-relaxed shadow-sm">
                    {m.query_text}
                  </div>
                  <div className="w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center font-bold text-xs text-white shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                </div>

                {/* AI Grounded Response */}
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-cyan-600 flex items-center justify-center font-bold text-xs text-white shrink-0 shadow-md shadow-cyan-500/20">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="space-y-3 max-w-xl">
                    <div className="bg-white/5 border border-white/5 p-4 rounded-2xl rounded-tl-sm text-xs text-gray-200 leading-relaxed space-y-2">
                      <p className="whitespace-pre-line">{m.response_text}</p>
                    </div>

                    {/* Citations Box */}
                    {m.citations && m.citations.length > 0 && (
                      <div className="space-y-1.5 pl-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1">
                          <CornerDownRight className="w-3 h-3" />
                          <span>Grounded Source Citations</span>
                        </span>
                        <div className="space-y-1.5">
                          {m.citations.map((c, i) => (
                            <div key={i} className="p-2.5 rounded-xl bg-cyan-950/20 border border-cyan-500/20 text-[11px] text-gray-300 space-y-0.5">
                              <div className="flex items-center justify-between font-semibold text-cyan-300">
                                <span>{c.document_title}</span>
                                <span>Page {c.page_number || 1} • {c.section_heading}</span>
                              </div>
                              <p className="text-[10px] text-gray-400 italic font-mono">"{c.passage_snippet}"</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-cyan-600 animate-pulse flex items-center justify-center text-white text-xs">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-white/5 border border-white/5 px-4 py-3 rounded-2xl text-xs text-gray-400 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                <span>Searching student notes and synthesizing grounded answer...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleAsk} className="pt-4 border-t border-white/5 flex items-center gap-3">
          <input
            type="text"
            required
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about your study materials..."
            className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-5 py-3 rounded-2xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 disabled:opacity-40 text-white font-semibold text-xs shadow-md shadow-violet-500/20 flex items-center gap-2 transition-all shrink-0"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
