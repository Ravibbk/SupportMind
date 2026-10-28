import { useState, useEffect } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Clock,
  DollarSign,
  AlertOctagon,
  RefreshCw,
} from 'lucide-react';
import type { PendingAction } from '../types';
import { fetchPendingActions, approveAction, rejectAction } from '../services/api';

interface ApprovalsQueueProps {
  onActionResolved?: () => void;
}

export const ApprovalsQueue = ({ onActionResolved }: ApprovalsQueueProps) => {
  const [actions, setActions] = useState<PendingAction[]>([]);

  const [loading, setLoading] = useState(false);
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'resolved'>('pending');

  const loadActions = async () => {
    setLoading(true);
    try {
      const data = await fetchPendingActions();
      setActions(data);
    } catch (err) {
      console.error('Error fetching actions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActions();
  }, []);

  const handleApprove = async (actionId: string) => {
    try {
      await approveAction(actionId);
      await loadActions();
      if (onActionResolved) onActionResolved();
    } catch (e) {
      alert(`Approval error: ${e}`);
    }
  };

  const handleConfirmReject = async (actionId: string) => {
    try {
      await rejectAction(actionId, rejectionReason || 'Supervisor rejected in queue');
      setRejectingId(null);
      setRejectionReason('');
      await loadActions();
      if (onActionResolved) onActionResolved();
    } catch (e) {
      alert(`Rejection error: ${e}`);
    }
  };

  const filteredActions = actions.filter((act) => {
    if (statusFilter === 'pending') return act.status === 'pending_approval';
    if (statusFilter === 'resolved') return act.status !== 'pending_approval';
    return true;
  });

  return (
    <div className="max-w-6xl w-full mx-auto p-4 sm:p-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-2xl border border-slate-800 shadow-xl backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-indigo-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              Human-in-the-Loop Supervisor Queue
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
              {actions.filter((a) => a.status === 'pending_approval').length} Pending
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Financial refunds and high-priority support escalations strictly mandate human supervisor sign-off.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-medium">
            <button
              onClick={() => setStatusFilter('pending')}
              className={`px-3 py-1.5 rounded-lg transition ${
                statusFilter === 'pending'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Pending ({actions.filter((a) => a.status === 'pending_approval').length})
            </button>
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-3 py-1.5 rounded-lg transition ${
                statusFilter === 'all'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              All Actions
            </button>
          </div>

          <button
            onClick={loadActions}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
            title="Refresh queue"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Action Cards List */}
      <div className="space-y-4">
        {filteredActions.length === 0 ? (
          <div className="bg-slate-900/40 rounded-2xl border border-slate-800 p-12 text-center">
            <CheckCircle2 className="w-12 h-12 text-emerald-400/60 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-200">All Queues Clear!</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
              There are currently no actions requiring supervisor review. Try asking the Copilot in the chat workspace:
              <br />
              <code className="text-indigo-400 bg-slate-950 px-2 py-0.5 rounded mt-2 inline-block">
                "My package ORD-10005 arrived damaged, please refund $49.99"
              </code>
            </p>
          </div>
        ) : (
          filteredActions.map((act) => {
            const isPending = act.status === 'pending_approval';
            const payload = act.payload || {};

            return (
              <div
                key={act.action_id}
                className={`p-5 rounded-2xl border transition-all duration-200 shadow-xl ${
                  isPending
                    ? 'bg-slate-900/80 border-indigo-500/40 shadow-indigo-500/5'
                    : 'bg-slate-900/40 border-slate-800 opacity-80'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-2">
                  <div className="flex items-center gap-3">
                    <div
                      className={`p-2 rounded-xl ${
                        act.action_type.includes('refund')
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                      }`}
                    >
                      {act.action_type.includes('refund') ? (
                        <DollarSign className="w-5 h-5" />
                      ) : (
                        <AlertOctagon className="w-5 h-5" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-bold text-white">
                          {act.action_id}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                          {act.action_type}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                        <Clock className="w-3 h-3" />
                        Initiated {act.created_at} (Session: {act.session_id})
                      </span>
                    </div>
                  </div>

                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
                      act.status === 'approved'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                        : act.status === 'rejected'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                        : 'bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse'
                    }`}
                  >
                    {act.status.replace('_', ' ')}
                  </span>
                </div>

                {/* Details Breakdown */}
                <div className="py-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  {Boolean(payload.order_id) && (
                    <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 font-medium block">Order ID</span>
                      <span className="text-indigo-400 font-mono font-semibold text-sm">
                        {String(payload.order_id)}
                      </span>
                    </div>
                  )}
                  {payload.refund_amount_usd !== undefined && (
                    <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 font-medium block">Requested Amount</span>
                      <span className="text-emerald-400 font-bold text-sm">
                        ${Number(payload.refund_amount_usd).toFixed(2)} USD
                      </span>
                    </div>
                  )}
                  {Boolean(payload.reason) && (
                    <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800 md:col-span-2">
                      <span className="text-slate-500 font-medium block">Customer Reason</span>
                      <span className="text-slate-200 italic">
                        "{String(payload.reason)}"
                      </span>
                    </div>
                  )}
                  {Boolean(payload.ticket_id) && (
                    <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 font-medium block">Escalation Ticket</span>
                      <span className="text-indigo-400 font-mono font-semibold text-sm">
                        {String(payload.ticket_id)}
                      </span>
                    </div>
                  )}
                </div>


                {/* Supervisor Action Buttons */}
                {isPending && (
                  <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-end gap-3">
                    {rejectingId === act.action_id ? (
                      <div className="flex-1 flex items-center gap-2 w-full">
                        <input
                          type="text"
                          value={rejectionReason}
                          onChange={(e) => setRejectionReason(e.target.value)}
                          placeholder="State supervisor rejection reason..."
                          className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
                        />
                        <button
                          onClick={() => handleConfirmReject(act.action_id)}
                          className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold"
                        >
                          Confirm Reject
                        </button>
                        <button
                          onClick={() => {
                            setRejectingId(null);
                            setRejectionReason('');
                          }}
                          className="px-2.5 py-1.5 bg-slate-800 text-slate-400 hover:text-white rounded-lg text-xs"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => setRejectingId(act.action_id)}
                          className="w-full sm:w-auto px-4 py-2 rounded-xl bg-slate-800 hover:bg-rose-500/20 hover:text-rose-400 text-slate-300 border border-slate-700 hover:border-rose-500/40 text-xs font-semibold transition flex items-center justify-center gap-1.5"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                          Reject Request
                        </button>
                        <button
                          onClick={() => handleApprove(act.action_id)}
                          className="w-full sm:w-auto px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-500/20 text-xs font-bold transition flex items-center justify-center gap-1.5"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Approve Fund Disbursement
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
