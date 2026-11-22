import React, { useState, useEffect } from 'react';
import { 
  X, CheckCircle, AlertTriangle, ArrowRight, RotateCcw, 
  BookOpen, Trophy, HelpCircle 
} from 'lucide-react';
import { fetchAssessment, submitAssessment } from '../services/api';
import 'katex/dist/katex.min.css';
import { BlockMath } from 'react-katex';

export default function AssessmentModal({ concept, isOpen, onClose, onComplete }) {
  const [loading, setLoading] = useState(true);
  const [quizData, setQuizData] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (isOpen && concept) {
      loadQuiz();
    }
  }, [isOpen, concept]);

  const loadQuiz = async () => {
    setLoading(true);
    setResult(null);
    setSelectedAnswers({});
    try {
      const data = await fetchAssessment(concept);
      setQuizData(data);
    } catch (err) {
      console.error('Failed to load assessment:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (questionId, optionId) => {
    if (result) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionId,
    }));
  };

  const handleSubmit = async () => {
    if (!quizData) return;
    setSubmitting(true);
    const answersList = Object.entries(selectedAnswers).map(([qid, opt]) => ({
      question_id: parseInt(qid),
      selected_option: opt,
    }));

    try {
      const res = await submitAssessment(concept, answersList);
      setResult(res);
      if (onComplete) onComplete(res);
    } catch (err) {
      console.error('Failed to submit assessment:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden text-slate-100">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
          <div>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Prerequisite Diagnostic Assessment
            </span>
            <h2 className="text-lg font-bold text-white mt-1">
              Readiness Check: <span className="text-indigo-400">{concept}</span>
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center gap-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
              <p className="text-xs text-slate-400">Assembling diagnostic questions from knowledge graph...</p>
            </div>
          ) : result ? (
            /* Results Screen */
            <div className="space-y-6 animate-fade-in">
              <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 flex items-center gap-5">
                <div
                  className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
                    result.passed ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                  }`}
                >
                  {result.passed ? <Trophy className="w-8 h-8" /> : <AlertTriangle className="w-8 h-8" />}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">
                    Score: {result.score_percentage}% ({result.correct_count}/{result.total_questions})
                  </h3>
                  <p className="text-xs text-slate-300 mt-1">
                    {result.passed
                      ? 'Excellent! You have solid foundational mastery of the prerequisite concepts.'
                      : 'You may struggle with this advanced topic until key prerequisites are reviewed.'}
                  </p>
                </div>
              </div>

              {/* Weak Prerequisites Alert */}
              {result.weak_prerequisites && result.weak_prerequisites.length > 0 && (
                <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                  <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" /> Recommended Revisions Needed
                  </h4>
                  <p className="text-xs text-slate-300 mb-2">
                    Review these prerequisite concepts before advancing to {concept}:
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {result.weak_prerequisites.map((p, i) => (
                      <span
                        key={i}
                        className="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2.5 py-1 rounded-md font-medium"
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Question Feedback */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Detailed Feedback</h4>
                {result.detailed_feedback.map((item, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border text-xs space-y-1.5 ${
                      item.is_correct
                        ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-200'
                        : 'bg-rose-950/20 border-rose-500/30 text-rose-200'
                    }`}
                  >
                    <div className="font-semibold flex items-center justify-between">
                      <span>Question {idx + 1} ({item.concept})</span>
                      <span>{item.is_correct ? '✓ Correct' : `✗ Correct answer: (${item.correct_option})`}</span>
                    </div>
                    <p className="text-slate-300">{item.question}</p>
                    <p className="text-slate-400 text-[11px] pt-1 border-t border-slate-800">
                      <strong>Explanation:</strong> {item.explanation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : quizData ? (
            /* Question List */
            <div className="space-y-6">
              {quizData.prerequisite_concepts && quizData.prerequisite_concepts.length > 0 && (
                <div className="text-xs text-slate-400 bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="font-semibold text-indigo-400">Prerequisites Tested:</span>{' '}
                  {quizData.prerequisite_concepts.join(', ')}
                </div>
              )}

              {quizData.questions.map((q, idx) => (
                <div key={q.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-indigo-400">
                      Question {idx + 1} &bull; {q.concept}
                    </span>
                  </div>
                  <p className="text-sm text-slate-200 font-medium">{q.question}</p>

                  {q.latex_formula && (
                    <div className="p-2 bg-slate-900 rounded-lg text-center">
                      <BlockMath math={q.latex_formula} />
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pt-1">
                    {q.options.map((opt) => {
                      const isSelected = selectedAnswers[q.id] === opt.id;
                      return (
                        <button
                          key={opt.id}
                          onClick={() => handleSelect(q.id, opt.id)}
                          className={`p-2.5 rounded-lg text-xs font-medium text-left border transition flex items-center gap-2 ${
                            isSelected
                              ? 'bg-indigo-600 border-indigo-500 text-white shadow-md'
                              : 'bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800'
                          }`}
                        >
                          <span className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center font-bold text-[10px]">
                            {opt.id}
                          </span>
                          <span>{opt.text}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400">No questions available for this concept.</p>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between">
          {result ? (
            <>
              <button
                onClick={loadQuiz}
                className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition"
              >
                <RotateCcw className="w-4 h-4" /> Try Again
              </button>
              <button
                onClick={onClose}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition"
              >
                Close & Return
              </button>
            </>
          ) : (
            <>
              <span className="text-xs text-slate-400">
                Answered: {Object.keys(selectedAnswers).length} / {quizData?.questions?.length || 0}
              </span>
              <button
                disabled={
                  submitting ||
                  !quizData ||
                  Object.keys(selectedAnswers).length < (quizData?.questions?.length || 1)
                }
                onClick={handleSubmit}
                className="flex items-center gap-2 px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold transition shadow-lg shadow-indigo-600/30"
              >
                {submitting ? 'Submitting...' : 'Submit Answers'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
