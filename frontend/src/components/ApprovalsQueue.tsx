import { useState, useEffect } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
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

  const pendingCount = actions.filter((a) => a.status === 'pending_approval').length;

  const filteredActions = actions.filter((act) => {
    if (statusFilter === 'pending') return act.status === 'pending_approval';
    if (statusFilter === 'resolved') return act.status !== 'pending_approval';
    return true;
  });

  return (
    <div className="max-w-6xl w-full mx-auto p-4 sm:p-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              Supervisor Approvals Queue
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
              {pendingCount} Pending
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Financial refunds and critical high-priority ticket escalations require supervisor sign-off before execution.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="flex bg-slate-100 p-0.5 rounded-lg text-xs font-medium">
            <button
              onClick={() => setStatusFilter('pending')}
              className={`px-3 py-1.5 rounded-md transition ${
                statusFilter === 'pending'
                  ? 'bg-white text-indigo-700 font-semibold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Pending ({pendingCount})
            </button>
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-3 py-1.5 rounded-md transition ${
                statusFilter === 'all'
                  ? 'bg-white text-indigo-700 font-semibold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              All Actions
            </button>
          </div>

          <button
            onClick={loadActions}
            disabled={loading}
            className="p-2 rounded-lg bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 transition"
            title="Refresh queue"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-indigo-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* Action Cards List */}
      <div className="space-y-4">
        {filteredActions.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-10 text-center shadow-xs">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
            <h3 className="text-sm font-semibold text-slate-900">All caught up</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              There are no pending actions currently awaiting supervisor review.
            </p>
          </div>
        ) : (
          filteredActions.map((act) => {
            const isPending = act.status === 'pending_approval';
            const payload = act.payload || {};

            return (
              <div
                key={act.action_id}
                className={`p-5 rounded-xl border bg-white transition-all shadow-xs ${
                  isPending ? 'border-amber-300' : 'border-slate-200'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 gap-2">
                  <div className="flex items-center gap-3">
                    <div
                      className={`p-2 rounded-lg ${
                        act.action_type.includes('refund')
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                      }`}
                    >
                      {act.action_type.includes('refund') ? (
                        <DollarSign className="w-4 h-4" />
                      ) : (
                        <AlertOctagon className="w-4 h-4" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-slate-900">
                          {act.action_id}
                        </span>
                        <span className="text-[11px] px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">
                          {act.action_type}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                        <Clock className="w-3 h-3" />
                        Initiated {act.created_at} • Session: {act.session_id}
                      </span>
                    </div>
                  </div>

                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold uppercase tracking-wider ${
                      act.status === 'approved'
                        ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                        : act.status === 'rejected'
                        ? 'bg-rose-50 text-rose-800 border border-rose-200'
                        : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}
                  >
                    {act.status.replace('_', ' ')}
                  </span>
                </div>

                {/* Details Breakdown */}
                <div className="py-3.5 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  {Boolean(payload.order_id) && (
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                      <span className="text-slate-500 font-medium block">Order ID</span>
                      <span className="text-slate-900 font-mono font-semibold text-sm">
                        {String(payload.order_id)}
                      </span>
                    </div>
                  )}
                  {payload.refund_amount_usd !== undefined && (
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                      <span className="text-slate-500 font-medium block">Requested Amount</span>
                      <span className="text-emerald-700 font-bold text-sm font-mono">
                        ${Number(payload.refund_amount_usd).toFixed(2)} USD
                      </span>
                    </div>
                  )}
                  {Boolean(payload.reason) && (
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 md:col-span-2">
                      <span className="text-slate-500 font-medium block">Customer Reason</span>
                      <span className="text-slate-800 italic">
                        "{String(payload.reason)}"
                      </span>
                    </div>
                  )}
                  {Boolean(payload.ticket_id) && (
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                      <span className="text-slate-500 font-medium block">Escalation Ticket</span>
                      <span className="text-indigo-700 font-mono font-semibold text-sm">
                        {String(payload.ticket_id)}
                      </span>
                    </div>
                  )}
                </div>

                {/* Supervisor Action Buttons */}
                {isPending && (
                  <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-end gap-2.5">
                    {rejectingId === act.action_id ? (
                      <div className="flex-1 flex items-center gap-2 w-full">
                        <input
                          type="text"
                          value={rejectionReason}
                          onChange={(e) => setRejectionReason(e.target.value)}
                          placeholder="State supervisor rejection reason..."
                          className="flex-1 bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-rose-500"
                        />
                        <button
                          onClick={() => handleConfirmReject(act.action_id)}
                          className="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold"
                        >
                          Confirm Reject
                        </button>
                        <button
                          onClick={() => setRejectingId(null)}
                          className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => setRejectingId(act.action_id)}
                          className="px-3.5 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-200 text-xs font-medium transition"
                        >
                          Reject Request
                        </button>
                        <button
                          onClick={() => handleApprove(act.action_id)}
                          className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-xs transition"
                        >
                          Approve Action
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
