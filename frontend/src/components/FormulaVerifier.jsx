import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, Calculator, Sparkles, ArrowRight } from 'lucide-react';
import { verifyExpression } from '../services/api';
import 'katex/dist/katex.min.css';
import { BlockMath, InlineMath } from 'react-katex';

export default function FormulaVerifier() {
  const [expression, setExpression] = useState('x^3 - 4*x');
  const [operation, setOperation] = useState('differentiate');
  const [variable, setVariable] = useState('x');
  const [targetEquals, setTargetEquals] = useState('3*x^2 - 4');
  const [lowerBound, setLowerBound] = useState('0');
  const [upperBound, setUpperBound] = useState('1');
  const [limitPoint, setLimitPoint] = useState('0');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await verifyExpression({
        expression,
        operation,
        variable,
        target_equals: targetEquals || null,
        lower_bound: operation === 'integrate' ? lowerBound : null,
        upper_bound: operation === 'integrate' ? upperBound : null,
        limit_point: operation === 'limit' ? limitPoint : null,
      });
      setResult(res);
    } catch (err) {
      console.error('Verification failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6 text-slate-100">
      <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
          <Calculator className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            SymPy Independent Mathematical Formula Verification
            <span className="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20 font-medium">
              Zero-Hallucination Symbolic Engine
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            Verify derivatives, integrals, algebraic equations, and trigonometric identities using formal computer algebra.
          </p>
        </div>
      </div>

      <form onSubmit={handleVerify} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Operation Selector */}
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Mathematical Operation</label>
            <select
              value={operation}
              onChange={(e) => setOperation(e.target.value)}
              className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="differentiate">Differentiate (Derivative)</option>
              <option value="integrate">Integrate (Integral)</option>
              <option value="solve">Solve Equation</option>
              <option value="limit">Evaluate Limit</option>
              <option value="equality_check">Check Mathematical Identity</option>
              <option value="simplify">Simplify Expression</option>
            </select>
          </div>

          {/* Main Expression Input */}
          <div className="md:col-span-2">
            <label className="text-xs font-semibold text-slate-400 block mb-1">
              Expression / LHS ({operation === 'solve' ? 'e.g. x^2 - 5x + 6 = 0' : 'e.g. x^3 + 2x'})
            </label>
            <input
              type="text"
              value={expression}
              onChange={(e) => setExpression(e.target.value)}
              placeholder="Enter mathematical expression..."
              className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
              required
            />
          </div>
        </div>

        {/* Dynamic Parameter Inputs based on operation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Variable</label>
            <input
              type="text"
              value={variable}
              onChange={(e) => setVariable(e.target.value)}
              className="w-full p-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          {(operation === 'differentiate' || operation === 'integrate' || operation === 'equality_check') && (
            <div className="md:col-span-2">
              <label className="text-xs font-semibold text-slate-400 block mb-1">
                Optional Target to Verify Equality Against (e.g. expected derivative)
              </label>
              <input
                type="text"
                value={targetEquals}
                onChange={(e) => setTargetEquals(e.target.value)}
                placeholder="Leave blank to compute directly, or specify target to verify..."
                className="w-full p-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>
          )}

          {operation === 'integrate' && (
            <>
              <div>
                <label className="text-xs font-semibold text-slate-400 block mb-1">Lower Bound (Optional)</label>
                <input
                  type="text"
                  value={lowerBound}
                  onChange={(e) => setLowerBound(e.target.value)}
                  placeholder="e.g. 0"
                  className="w-full p-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-400 block mb-1">Upper Bound (Optional)</label>
                <input
                  type="text"
                  value={upperBound}
                  onChange={(e) => setUpperBound(e.target.value)}
                  placeholder="e.g. 1 or pi"
                  className="w-full p-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>
            </>
          )}

          {operation === 'limit' && (
            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1">Limit Point (x -&gt; a)</label>
              <input
                type="text"
                value={limitPoint}
                onChange={(e) => setLimitPoint(e.target.value)}
                placeholder="e.g. 0, oo"
                className="w-full p-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold transition shadow-lg shadow-indigo-600/30"
        >
          {loading ? 'Verifying symbolically with SymPy...' : 'Verify Expression with SymPy'}
          <ArrowRight className="w-4 h-4" />
        </button>
      </form>

      {/* Verification Result Card */}
      {result && (
        <div
          className={`p-5 rounded-2xl border transition-all ${
            result.verified
              ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-200'
              : 'bg-rose-950/20 border-rose-500/40 text-rose-200'
          }`}
        >
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-3">
            <div className="flex items-center gap-2">
              {result.verified ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-rose-400" />
              )}
              <span className="font-bold text-sm">
                {result.verified ? 'SymPy Verification: VALID & VERIFIED' : 'SymPy Verification: CANNOT BE VERIFIED / REFUTED'}
              </span>
            </div>
            <span className="text-xs font-mono bg-slate-900 px-2.5 py-1 rounded-md text-slate-300">
              Operation: {result.operation}
            </span>
          </div>

          <div className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 text-center my-3">
            {result.latex_output ? (
              <BlockMath math={result.latex_output} />
            ) : (
              <span className="font-mono text-sm">{result.symbolic_result}</span>
            )}
          </div>

          <p className="text-xs text-slate-300">{result.message}</p>
        </div>
      )}
    </div>
  );
}
