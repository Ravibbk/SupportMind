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

  const getDirectionText = (metric: string) => {
    if (metric.includes('Latency') || metric.includes('Cost')) {
      return 'Lower is better';
    }
    return 'Higher is better';
  };

  return (
    <div className="max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              RAG & Retrieval Evaluation Lab
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              60 Grounded Test Cases
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Empirically measuring retrieval hit-rate, mean reciprocal rank (MRR), correctness, and latency across 7 pipeline variants.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
          <div className="text-left">
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">
              Optimal Pipeline
            </span>
            <span className="text-xs font-bold text-indigo-700">
              Hybrid + Reranker (v3)
            </span>
          </div>
        </div>
      </div>

      {/* Metric Selector Tabs */}
      <div className="flex flex-wrap items-center gap-2 bg-white p-2 rounded-xl border border-slate-200 shadow-xs">
        <span className="text-xs font-semibold text-slate-500 ml-2 mr-1">
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
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              selectedMetric === metric
                ? 'bg-indigo-50 text-indigo-700 font-semibold border border-indigo-200'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            {metric}
          </button>
        ))}
      </div>

      {/* Visual Bar Comparison Chart */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-indigo-600" />
            Comparison: {selectedMetric}
          </h3>
          <span className="text-xs text-slate-500 font-medium">
            {getDirectionText(selectedMetric)}
          </span>
        </div>

        <div className="space-y-3.5 pt-2">
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
                        isProd ? 'text-indigo-900 font-semibold' : 'text-slate-700'
                      }`}
                    >
                      {rec.Configuration}
                    </span>
                    {isProd && (
                      <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                        Production
                      </span>
                    )}
                  </div>
                  <span className="font-mono font-semibold text-slate-900">
                    {rawVal}
                    {selectedMetric.includes('Latency') ? ' ms' : ''}
                  </span>
                </div>
                <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden border border-slate-200">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${
                      isProd
                        ? 'bg-indigo-600'
                        : rec.Configuration.includes('LLM Only')
                        ? 'bg-rose-400'
                        : 'bg-slate-300'
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
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-indigo-600" />
            <h4 className="text-sm font-semibold text-slate-900">
              Benchmark Summary Matrix
            </h4>
          </div>
          <span className="text-xs text-slate-500 font-mono">
            eval/results/benchmark_summary.csv
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[11px] border-b border-slate-200 font-semibold">
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
            <tbody className="divide-y divide-slate-100">
              {records.map((r, i) => {
                const isProd = r.Configuration.includes('Production');
                return (
                  <tr
                    key={i}
                    className={`hover:bg-slate-50/80 transition ${
                      isProd ? 'bg-indigo-50/30' : ''
                    }`}
                  >
                    <td className="py-3.5 px-4 font-medium text-slate-900">
                      {r.Configuration}
                    </td>
                    <td className="py-3.5 px-4 font-mono">{r['Hit-Rate@4']}</td>
                    <td className="py-3.5 px-4 font-mono">{r['MRR']}</td>
                    <td className="py-3.5 px-4 font-mono font-semibold text-emerald-700">
                      {r['Answer Correctness']}
                    </td>
                    <td className="py-3.5 px-4 font-mono">{r['Latency (p50 ms)']} ms</td>
                    <td className="py-3.5 px-4 font-mono">${r['Cost ($/1000q)']}</td>
                    <td className="py-3.5 px-4 text-slate-500">{r['Key Innovation']}</td>
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
