import { useState, useEffect } from 'react';
import {
  Package,
  Search,
  Filter,
  Truck,
  CheckCircle,
  AlertCircle,
  Clock,
  ChevronLeft,
  ChevronRight,
  MessageSquare,
} from 'lucide-react';

import type { Order } from '../types';
import { fetchOrders } from '../services/api';

interface OrdersTableProps {
  onSelectOrderForChat?: (orderId: string) => void;
}

export const OrdersTable = ({ onSelectOrderForChat }: OrdersTableProps) => {
  const [orders, setOrders] = useState<Order[]>([]);

  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [limit] = useState(15);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const data = await fetchOrders(query, statusFilter || undefined, limit, offset);
      setOrders(data);
    } catch (e) {
      console.error('Error fetching orders:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, [statusFilter, offset]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setOffset(0);
    loadOrders();
  };

  const getStatusBadge = (status: string) => {
    const s = status.toLowerCase();
    if (s === 'delivered') {
      return (
        <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <CheckCircle className="w-3 h-3" />
          Delivered
        </span>
      );
    }
    if (s === 'in transit') {
      return (
        <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
          <Truck className="w-3 h-3" />
          In Transit
        </span>
      );
    }
    if (s === 'delayed') {
      return (
        <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          <Clock className="w-3 h-3" />
          Delayed
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
        <AlertCircle className="w-3 h-3" />
        {status}
      </span>
    );
  };

  return (
    <div className="max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-5">
      {/* Search & Filter Header */}
      <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 shadow-xl backdrop-blur-md flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              NovaCart Fulfillment Database
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              500 Seeded Orders
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real parameterized SQLite records queried safely by the Copilot Data Agent.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
          <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by ID, customer..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </form>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-500" />
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setOffset(0);
              }}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Statuses</option>
              <option value="Delivered">Delivered</option>
              <option value="In Transit">In Transit</option>
              <option value="Delayed">Delayed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-slate-900/60 rounded-2xl border border-slate-800 shadow-xl overflow-hidden backdrop-blur-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Product</th>
                <th className="py-3 px-4">Price</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Est. Delivery</th>
                <th className="py-3 px-4">Carrier</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-slate-500">
                    Loading orders...
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-slate-500">
                    No orders matching your criteria.
                  </td>
                </tr>
              ) : (
                orders.map((o) => (
                  <tr
                    key={o.order_id}
                    className="hover:bg-slate-800/40 transition duration-150"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-indigo-400">
                      {o.order_id}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium text-slate-200">{o.customer_name}</div>
                      <div className="text-[10px] text-slate-500">{o.email}</div>
                    </td>
                    <td className="py-3 px-4 max-w-xs truncate text-slate-300" title={o.product_title}>
                      {o.product_title}
                    </td>
                    <td className="py-3 px-4 font-mono font-semibold text-slate-100">
                      ${o.price_usd.toFixed(2)}
                    </td>
                    <td className="py-3 px-4">{getStatusBadge(o.status)}</td>
                    <td className="py-3 px-4 text-slate-400">{o.expected_delivery}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[10px]">
                        {o.carrier}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {onSelectOrderForChat && (
                        <button
                          onClick={() => onSelectOrderForChat(o.order_id)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 transition text-[11px] font-medium"
                          title="Ask Copilot about this order"
                        >
                          <MessageSquare className="w-3 h-3" />
                          <span>Track</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="flex items-center justify-between p-3.5 bg-slate-950/60 border-t border-slate-800 text-xs text-slate-400">
          <span>
            Showing rows {offset + 1} to {offset + orders.length}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setOffset((prev) => Math.max(0, prev - limit))}
              disabled={offset === 0 || loading}
              className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setOffset((prev) => prev + limit)}
              disabled={orders.length < limit || loading}
              className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
