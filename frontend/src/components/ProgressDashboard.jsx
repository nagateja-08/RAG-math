import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, Award, AlertCircle, CheckCircle, Clock, 
  BookOpen, ArrowRight, Sparkles, RefreshCw 
} from 'lucide-react';
import { fetchProgress } from '../services/api';

export default function ProgressDashboard({ onSelectTopic, onStartQuiz }) {
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    setLoading(true);
    try {
      const data = await fetchProgress('default_student');
      setProgress(data);
    } catch (err) {
      console.error('Failed to load student progress:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="w-full h-96 flex flex-col items-center justify-center gap-3 bg-slate-950 border border-slate-800 rounded-2xl">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
        <span className="text-xs text-slate-400">Loading your learning analytics...</span>
      </div>
    );
  }

  if (!progress) {
    return (
      <div className="p-8 text-center text-slate-400 bg-slate-950 border border-slate-800 rounded-2xl">
        No learning activity recorded yet. Ask a math question or take a diagnostic quiz!
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Metric Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Questions Attempted */}
        <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-2xl flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-white">{progress.total_questions_asked}</div>
            <div className="text-xs text-slate-400">Questions Asked</div>
          </div>
        </div>

        {/* Concepts Mastered */}
        <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-2xl flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-white">{progress.concepts_mastered}</div>
            <div className="text-xs text-slate-400">Concepts Mastered</div>
          </div>
        </div>

        {/* Average Quiz Score */}
        <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-2xl flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-white">{progress.average_assessment_score}%</div>
            <div className="text-xs text-slate-400">Quiz Average</div>
          </div>
        </div>

        {/* Weak Concepts Count */}
        <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-2xl flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-white">{progress.weak_concepts.length}</div>
            <div className="text-xs text-slate-400">Areas for Review</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Subject Mastery Progress Bars */}
        <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-indigo-400" /> Mastery by Subject Area
            </h3>
            <button onClick={loadProgress} className="text-slate-400 hover:text-white p-1">
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3 pt-1">
            {Object.keys(progress.mastery_by_subject || {}).length > 0 ? (
              Object.entries(progress.mastery_by_subject).map(([subject, score]) => (
                <div key={subject} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-medium text-slate-300">{subject}</span>
                    <span className="text-indigo-400 font-semibold">{score}%</span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, Math.max(5, score))}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 py-4 text-center">
                Study concepts across Calculus, Algebra, or Probability to see your mastery scores!
              </div>
            )}
          </div>
        </div>

        {/* Recommended Next Topics (Knowledge Graph Grounded) */}
        <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-400" /> Recommended Study Path
          </h3>
          <p className="text-xs text-slate-300">
            Based on your identified prerequisites and knowledge graph dependencies:
          </p>

          <div className="flex flex-wrap gap-2 pt-2">
            {progress.recommended_study_plan.map((topic, idx) => (
              <button
                key={idx}
                onClick={() => onSelectTopic && onSelectTopic(topic)}
                className="group flex items-center gap-2 px-3 py-2 bg-slate-950 hover:bg-indigo-600 border border-slate-800 hover:border-indigo-500 text-slate-200 hover:text-white rounded-xl text-xs font-medium transition shadow-sm"
              >
                <span>{topic}</span>
                <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
              </button>
            ))}
          </div>

          {progress.weak_concepts.length > 0 && (
            <div className="pt-3 border-t border-slate-800">
              <span className="text-[11px] text-amber-400 font-semibold uppercase tracking-wider block mb-1.5">
                Priority Review (Failed Diagnostic Checks):
              </span>
              <div className="flex flex-wrap gap-1.5">
                {progress.weak_concepts.map((weak, i) => (
                  <button
                    key={i}
                    onClick={() => onStartQuiz && onStartQuiz(weak)}
                    className="text-xs bg-amber-500/10 text-amber-300 border border-amber-500/20 px-2.5 py-1 rounded-lg hover:bg-amber-500/20 transition flex items-center gap-1.5"
                  >
                    <span>{weak}</span>
                    <span className="text-[10px] text-amber-400/80">&bull; Retest</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Question Activity Table */}
      <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl space-y-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400" /> Recent Learning Inquiries
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-2.5 px-4 rounded-l-lg">Question</th>
                <th className="py-2.5 px-4">Concept</th>
                <th className="py-2.5 px-4">Subject</th>
                <th className="py-2.5 px-4">SymPy Verified</th>
                <th className="py-2.5 px-4 rounded-r-lg">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {progress.recent_activity.length > 0 ? (
                progress.recent_activity.map((act, i) => (
                  <tr key={i} className="hover:bg-slate-800/30 transition">
                    <td className="py-2.5 px-4 font-medium text-slate-200 max-w-xs truncate">{act.question}</td>
                    <td className="py-2.5 px-4 text-indigo-400">{act.concept}</td>
                    <td className="py-2.5 px-4">{act.subject}</td>
                    <td className="py-2.5 px-4">
                      {act.verified ? (
                        <span className="text-emerald-400 font-semibold">✓ Verified</span>
                      ) : (
                        <span className="text-slate-500">Conceptual</span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">{act.timestamp}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-4 text-center text-slate-500">
                    No inquiries recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
