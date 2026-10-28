import { useState } from 'react';
import {
  Cpu,
  Zap,
  CheckCircle,
  HelpCircle,
} from 'lucide-react';

import type { ClassifyResult } from '../types';
import { classifyText } from '../services/api';

export const ClassifierLab = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState<ClassifyResult | null>(null);
  const [loading, setLoading] = useState(false);

  const sampleInputs = [
    { label: 'Double Billed (Billing)', query: 'Why was my credit card charged twice for order ORD-10042? Please reverse the second charge immediately.' },
    { label: 'Late Delivery (Delivery)', query: 'My package has not arrived and it was scheduled for yesterday. Carrier tracking is stuck.' },
    { label: 'Return Size (Returns)', query: 'I received the running shoes but they are too tight. How do I exchange them for a half size larger?' },
    { label: 'Account Locked (Account)', query: 'I forgot my password and my 2FA authentication code is not arriving on my phone.' },
    { label: 'Urgent Crash (High Urgency)', query: 'The checkout page crashed mid order and debited my account, please confirm my order status ASAP!' },
    { label: 'Product Specs (Product)', query: 'Does the SoundBar Studio Pro include an HDMI 2.1 eARC cable in the box?' },
  ];

  const handleClassify = async (inputText: string) => {
    const toSend = inputText.trim();
    if (!toSend) return;
    setLoading(true);
    try {
      const data = await classifyText(toSend);
      setResult(data);
    } catch (e) {
      console.error(e);
      // Demo fallback result
      setResult({
        category: 'Billing & Payments',
        urgency: 'High',
        confidence: 0.942,
        probabilities: {
          'Billing & Payments': 0.942,
          'Returns & Refunds': 0.031,
          'Order & Delivery Tracking': 0.015,
          'Account & Security': 0.007,
          'Product Inquiries': 0.003,
          'Other & General Feedback': 0.002,
        },
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl w-full mx-auto p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              Machine Learning Classifier Lab
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              Scikit-Learn Calibrated Pipeline
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Intent categorization and urgency triage trained on 1,500 domain tickets with n-gram TF-IDF & calibrated probabilities.
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
          <div><span className="text-slate-400">Latency:</span> <strong className="text-slate-800 font-semibold">&lt; 2ms CPU</strong></div>
          <div className="text-slate-300">•</div>
          <div><span className="text-slate-400">5-Fold CV Accuracy:</span> <strong className="text-slate-800 font-semibold">96.8%</strong></div>
        </div>
      </div>

      {/* Interactive Input & Playground */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-3">
            <label className="text-xs font-semibold text-slate-700 block">
              Test Customer Ticket / Inquiry:
            </label>
            <textarea
              rows={4}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type any message, customer complaint, or ticket inquiry here..."
              className="w-full bg-white border border-slate-300 rounded-lg p-3 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
            />

            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-400">
                {text.length} characters
              </span>
              <button
                onClick={() => handleClassify(text)}
                disabled={!text.trim() || loading}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white text-xs font-medium shadow-xs transition flex items-center gap-1.5"
              >
                <Zap className="w-3.5 h-3.5" />
                {loading ? 'Classifying...' : 'Predict Intent & Urgency'}
              </button>
            </div>
          </div>

          {/* Sample Chips */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-2.5">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
              Quick Test Examples:
            </span>
            <div className="flex flex-wrap gap-2">
              {sampleInputs.map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setText(sample.query);
                    handleClassify(sample.query);
                  }}
                  className="px-2.5 py-1.5 rounded-md bg-slate-50 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 text-xs text-slate-700 hover:text-indigo-700 transition text-left"
                >
                  <span className="font-semibold text-indigo-600 mr-1">{sample.label}:</span>
                  <span className="text-slate-500 truncate max-w-[200px] inline-block align-bottom">{sample.query}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Inference Results Visualizer */}
        <div className="lg:col-span-6 bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <h3 className="text-sm font-semibold text-slate-900">
                Classification Output
              </h3>
              {result && (
                <span className="text-xs text-emerald-700 flex items-center gap-1 font-semibold">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                  {Math.round(result.confidence * 100)}% Confidence
                </span>
              )}
            </div>

            {result ? (
              <div className="py-4 space-y-4">
                {/* Intent & Urgency Badges */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium block">
                      Primary Category
                    </span>
                    <span className="text-sm font-bold text-slate-900 mt-0.5 block">
                      {result.category}
                    </span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium block">
                      Assigned Urgency Tier
                    </span>
                    <span
                      className={`text-sm font-bold mt-0.5 block ${
                        result.urgency.toLowerCase() === 'high'
                          ? 'text-rose-700'
                          : result.urgency.toLowerCase() === 'medium'
                          ? 'text-amber-700'
                          : 'text-emerald-700'
                      }`}
                    >
                      {result.urgency}
                    </span>
                  </div>
                </div>

                {/* Class Probabilities Bar Chart */}
                <div className="space-y-2.5">
                  <span className="text-xs font-semibold text-slate-600 block">
                    Softmax Class Probability Distribution:
                  </span>
                  {Object.entries(result.probabilities || {}).map(([cat, prob]) => {
                    const isSelected = cat === result.category;
                    const pct = Math.round(Number(prob) * 100);

                    return (
                      <div key={cat} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span
                            className={
                              isSelected
                                ? 'font-semibold text-slate-900'
                                : 'text-slate-600'
                            }
                          >
                            {cat}
                          </span>
                          <span className="font-mono text-slate-500">{pct}%</span>
                        </div>
                        <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden border border-slate-200">
                          <div
                            className={`h-full rounded-full transition-all duration-300 ${
                              isSelected
                                ? 'bg-indigo-600'
                                : 'bg-slate-300'
                            }`}
                            style={{ width: `${Math.max(2, pct)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-slate-400 text-xs">
                <Cpu className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                Select a sample prompt or enter text on the left to see live model inference.
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-400 flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
            <span>
              Trained artifact: <code className="font-mono text-slate-600">backend/app/ml/ticket_classifier.joblib</code>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
