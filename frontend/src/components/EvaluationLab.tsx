import { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  FileSpreadsheet,
} from 'lucide-react';
import type { EvalRecord } from '../types';
import { fetchEvalResults } from '../services/api';

export const EvaluationLab = () => {
  const [records, setRecords] = useState<EvalRecord[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<
    'Hit-Rate@4' | 'MRR' | 'Answer Correctness' | 'Latency (p50 ms)' | 'Cost ($/1000q)'
  >('Answer Correctness');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchEvalResults();
        setRecords(data);
      } catch (err) {
        console.error('Error fetching eval benchmark data:', err);
      }
    };
    load();
  }, []);


  const getMetricNumber = (val: string) => {
    const n = parseFloat(val);
    return isNaN(n) ? 0 : n;
  };

  return (
    <div className="max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 shadow-xl backdrop-blur-md flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-indigo-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              RAG & Prompt Evaluation Lab
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
              60 Grounded Benchmark Test Cases
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Empirically measuring retrieval hit rate, mean reciprocal rank, faithfulness, and latency trade-offs across 7 pipeline variants.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">
              Winning Architecture
            </span>
            <span className="text-sm font-bold text-emerald-400">
              Hybrid + Reranker (v3)
            </span>
          </div>
        </div>
      </div>

      {/* Metric Selector Tabs */}
      <div className="flex flex-wrap items-center gap-2 bg-slate-900/40 p-2 rounded-xl border border-slate-800">
        <span className="text-xs font-semibold text-slate-400 ml-2 mr-1">
          Compare Metric:
        </span>
        {(
          [
            'Answer Correctness',
            'Hit-Rate@4',
            'MRR',
            'Latency (p50 ms)',
            'Cost ($/1000q)',
          ] as const
        ).map((metric) => (
          <button
            key={metric}
            onClick={() => setSelectedMetric(metric)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              selectedMetric === metric
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            {metric}
          </button>
        ))}
      </div>

      {/* Visual Bar Comparison Chart */}
      <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            Empirical Comparison: {selectedMetric}
          </h3>
          <span className="text-xs text-slate-400">Higher is better (except latency & cost)</span>
        </div>

        <div className="space-y-3 pt-2">
          {records.map((rec, i) => {
            const rawVal = rec[selectedMetric];
            const numVal = getMetricNumber(rawVal);
            const isProd = rec.Configuration.includes('Production');

            // Normalize for visual progress bar
            let barWidth = 0;
            if (selectedMetric === 'Latency (p50 ms)') {
              barWidth = Math.min(100, Math.max(5, (numVal / 700) * 100));
            } else if (selectedMetric === 'Cost ($/1000q)') {
              barWidth = Math.min(100, Math.max(5, (numVal / 1.5) * 100));
            } else {
              barWidth = Math.min(100, Math.max(5, numVal * 100));
            }

            return (
              <div key={i} className="space-y-1">
                <div className="flex justify-between items-center text-xs">
                  <div className="flex items-center gap-2">
                    <span
                      className={`font-medium ${
                        isProd ? 'text-indigo-300 font-bold' : 'text-slate-300'
                      }`}
                    >
                      {rec.Configuration}
                    </span>
                    {isProd && (
                      <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                        Active
                      </span>
                    )}
                  </div>
                  <span className="font-mono font-bold text-slate-100">
                    {rawVal}
                    {selectedMetric.includes('Latency') ? ' ms' : ''}
                  </span>
                </div>
                <div className="w-full h-3 rounded-full bg-slate-950 overflow-hidden border border-slate-800">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isProd
                        ? 'bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-400'
                        : rec.Configuration.includes('LLM Only')
                        ? 'bg-rose-500/70'
                        : 'bg-slate-600'
                    }`}
                    style={{ width: `${barWidth}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Comprehensive Benchmark Table */}
      <div className="bg-slate-900/60 rounded-2xl border border-slate-800 shadow-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-indigo-400" />
            <h4 className="text-sm font-bold text-slate-200">
              Evaluation Matrix Benchmark Summary
            </h4>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            eval/results/benchmark_summary.csv
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Configuration</th>
                <th className="py-3 px-4">Hit-Rate@4</th>
                <th className="py-3 px-4">MRR</th>
                <th className="py-3 px-4">Correctness</th>
                <th className="py-3 px-4">p50 Latency</th>
                <th className="py-3 px-4">Cost / 1k</th>
                <th className="py-3 px-4">Key Architectural Innovation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {records.map((r, i) => {
                const isProd = r.Configuration.includes('Production');
                return (
                  <tr
                    key={i}
                    className={`hover:bg-slate-800/40 transition ${
                      isProd ? 'bg-indigo-950/20' : ''
                    }`}
                  >
                    <td className="py-3 px-4 font-medium text-slate-200">
                      {r.Configuration}
                    </td>
                    <td className="py-3 px-4 font-mono">{r['Hit-Rate@4']}</td>
                    <td className="py-3 px-4 font-mono">{r['MRR']}</td>
                    <td className="py-3 px-4 font-mono font-bold text-emerald-400">
                      {r['Answer Correctness']}
                    </td>
                    <td className="py-3 px-4 font-mono">{r['Latency (p50 ms)']} ms</td>
                    <td className="py-3 px-4 font-mono">${r['Cost ($/1000q)']}</td>
                    <td className="py-3 px-4 text-slate-400">{r['Key Innovation']}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
