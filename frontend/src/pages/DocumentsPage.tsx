import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileText,
  Trash2,
  Eye,
  PlusCircle,
  Search,
  CheckCircle,
  Clock,
  AlertCircle,
  BookOpen,
  Sparkles,
  X
} from 'lucide-react';
import { apiFetch, getStoredToken } from '../lib/api';
import { DocumentItem, DocumentDetail, DocumentSummary } from '../types';

export const DocumentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedSummary, setSelectedSummary] = useState<DocumentSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [previewDoc, setPreviewDoc] = useState<DocumentDetail | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const fetchDocs = async () => {
    try {
      const data = await apiFetch<DocumentItem[]>('/documents');
      setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowed = ['.pdf', '.docx', '.pptx', '.txt'];
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowed.includes(ext)) {
      alert(`Invalid format. Allowed formats: ${allowed.join(', ')}`);
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name.replace(/\.[^/.]+$/, ''));

    setUploading(true);
    setUploadProgress(40);

    try {
      const token = getStoredToken();
      const res = await fetch('/api/documents/upload', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }

      setUploadProgress(100);
      await fetchDocs();
    } catch (err: any) {
      alert(err.message || 'Error uploading document');
    } finally {
      setUploading(false);
      setUploadProgress(0);
      e.target.value = '';
    }
  };

  const handleDelete = async (docId: number) => {
    if (!window.confirm('Delete this study material and all its chunks?')) return;
    try {
      await apiFetch(`/documents/${docId}`, { method: 'DELETE' });
      setDocuments(documents.filter((d) => d.id !== docId));
    } catch (err: any) {
      alert(err.message || 'Delete failed');
    }
  };

  const handleOpenSummary = async (docId: number) => {
    setSummaryLoading(true);
    try {
      const summary = await apiFetch<DocumentSummary>(`/documents/${docId}/summary`);
      setSelectedSummary(summary);
    } catch (err) {
      alert('Could not load summary');
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleOpenPreview = async (docId: number) => {
    setPreviewLoading(true);
    try {
      const detail = await apiFetch<DocumentDetail>(`/documents/${docId}`);
      setPreviewDoc(detail);
    } catch (err) {
      alert('Could not load preview');
    } finally {
      setPreviewLoading(false);
    }
  };

  const filtered = documents.filter((d) =>
    d.title.toLowerCase().includes(search.toLowerCase()) ||
    d.file_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8 pb-12">
      {/* Top Title & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">Smart Document Studio</h1>
          <p className="text-xs text-gray-400 mt-1">
            Upload course materials to extract content, detect key topics, and generate grounded exams.
          </p>
        </div>

        {/* Upload Trigger Input */}
        <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium text-xs shadow-md shadow-violet-500/25 transition-all">
          <UploadCloud className="w-4 h-4" />
          <span>{uploading ? 'Processing Document...' : 'Upload Study Material'}</span>
          <input
            type="file"
            className="hidden"
            accept=".pdf,.docx,.pptx,.txt"
            disabled={uploading}
            onChange={handleFileUpload}
          />
        </label>
      </div>

      {/* Drag & Drop Visual Box */}
      <div className="glass-panel p-8 rounded-3xl border-dashed border-2 border-white/10 hover:border-violet-500/40 text-center relative transition-all group">
        <div className="max-w-md mx-auto space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-violet-950/60 border border-violet-500/20 text-violet-400 mx-auto flex items-center justify-center group-hover:scale-110 transition-transform">
            <UploadCloud className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Drop lecture notes or textbooks here</h3>
            <p className="text-xs text-gray-400 mt-1">Supports PDF, DOCX, PPTX slides, and plain TXT (Max 35MB)</p>
          </div>
          {uploading && (
            <div className="pt-2 max-w-xs mx-auto space-y-1">
              <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-violet-500 to-cyan-400 animate-pulse w-3/4" />
              </div>
              <span className="text-[10px] text-cyan-400 font-mono">Extracting semantic chunks & AI topics...</span>
            </div>
          )}
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative w-full max-w-xs">
          <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Filter uploaded materials..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-violet-500/50"
          />
        </div>
        <span className="text-xs text-gray-400 font-medium">
          {filtered.length} {filtered.length === 1 ? 'Material' : 'Materials'} Uploaded
        </span>
      </div>

      {/* Document Grid */}
      {loading ? (
        <div className="text-center py-12 text-gray-400">Loading your study documents...</div>
      ) : filtered.length === 0 ? (
        <div className="glass-panel p-12 rounded-3xl text-center space-y-3">
          <FileText className="w-8 h-8 text-gray-500 mx-auto" />
          <h3 className="text-sm font-semibold text-gray-300">No documents found</h3>
          <p className="text-xs text-gray-500">Upload your first syllabus notes above to start generating tests.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((doc) => (
            <div
              key={doc.id}
              className="glass-card-interactive p-6 rounded-2xl flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded uppercase text-[10px] font-bold bg-violet-950 border border-violet-500/30 text-violet-300">
                      {doc.file_type}
                    </span>
                    <span className="text-[11px] text-gray-400">{doc.page_count} Pages</span>
                  </div>
                  <span className={`flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    doc.processing_status === 'completed'
                      ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/20'
                      : (doc.processing_status === 'failed' ? 'bg-red-950/60 text-red-400' : 'bg-amber-950/60 text-amber-400')
                  }`}>
                    {doc.processing_status === 'completed' ? <CheckCircle className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                    {doc.processing_status.toUpperCase()}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white line-clamp-2">{doc.title}</h3>
                <p className="text-[11px] text-gray-400 line-clamp-1">{doc.file_name}</p>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 border-t border-white/5 flex items-center justify-between gap-2">
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleOpenSummary(doc.id)}
                    title="View AI Summary"
                    className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 hover:text-cyan-400 transition-colors"
                  >
                    <BookOpen className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleOpenPreview(doc.id)}
                    title="Preview Chunks"
                    className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 hover:text-violet-400 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    title="Delete Material"
                    className="p-2 rounded-xl bg-white/5 hover:bg-red-950/40 text-gray-400 hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <button
                  onClick={() => navigate(`/tests/create?docId=${doc.id}`)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-violet-600/20 hover:bg-violet-600/30 border border-violet-500/30 text-xs font-semibold text-violet-300 transition-colors"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  <span>Create Exam</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Document AI Summary Modal */}
      {selectedSummary && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-white/10 w-full max-w-2xl rounded-3xl p-6 sm:p-8 space-y-6 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold">
                <Sparkles className="w-4 h-4" />
                <span>AI Material Synthesis</span>
              </div>
              <button
                onClick={() => setSelectedSummary(null)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div>
              <h2 className="text-xl font-bold text-white">{selectedSummary.title}</h2>
              <p className="text-xs text-gray-400 mt-1">Verified Extract ({selectedSummary.page_count} Pages)</p>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-300">Executive Summary</h4>
              <p className="text-xs text-gray-300 leading-relaxed bg-white/5 p-4 rounded-xl border border-white/5">
                {selectedSummary.summary_text}
              </p>
            </div>

            {/* Key Concepts */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-300">Key Concepts & Definitions</h4>
              <div className="grid grid-cols-1 gap-2.5">
                {selectedSummary.key_concepts.map((kc, i) => (
                  <div key={i} className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1">
                    <span className="text-xs font-semibold text-violet-300">{kc.term}</span>
                    <p className="text-xs text-gray-400">{kc.definition}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 flex justify-end gap-3">
              <button
                onClick={() => setSelectedSummary(null)}
                className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-gray-300"
              >
                Close
              </button>
              <button
                onClick={() => {
                  const docId = selectedSummary.id;
                  setSelectedSummary(null);
                  navigate(`/tests/create?docId=${docId}`);
                }}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-xs font-semibold text-white shadow-md shadow-violet-500/25"
              >
                Generate Exam From Document
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chunks Preview Modal */}
      {previewDoc && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-white/10 w-full max-w-3xl rounded-3xl p-6 sm:p-8 space-y-6 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">{previewDoc.title}</h2>
                <p className="text-xs text-gray-400">Extracted Chunks ({previewDoc.chunks.length} Total)</p>
              </div>
              <button
                onClick={() => setPreviewDoc(null)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {previewDoc.chunks.map((c) => (
                <div key={c.id} className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
                  <div className="flex items-center justify-between text-[11px] text-cyan-400 font-mono">
                    <span>Page {c.page_number} • {c.section_heading}</span>
                    <span>~{c.token_count} words</span>
                  </div>
                  <p className="text-xs text-gray-300 leading-relaxed font-sans">{c.content}</p>
                </div>
              ))}
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setPreviewDoc(null)}
                className="px-4 py-2 rounded-xl bg-white/10 text-xs font-semibold text-gray-200"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
