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
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          <CheckCircle className="w-3 h-3" />
          Delivered
        </span>
      );
    }
    if (s === 'in transit') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-sky-50 text-sky-700 border border-sky-200">
          <Truck className="w-3 h-3" />
          In Transit
        </span>
      );
    }
    if (s === 'delayed') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200">
          <Clock className="w-3 h-3" />
          Delayed
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
        <AlertCircle className="w-3 h-3" />
        {status}
      </span>
    );
  };

  return (
    <div className="max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-5">
      {/* Search & Filter Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              Fulfillment Orders
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
              500 Orders
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Search, filter, and track customer shipments queried safely by the Copilot Data Agent.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-2.5 w-full md:w-auto">
          <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by ID, customer..."
              className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
            />
          </form>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setOffset(0);
              }}
              className="bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-700 focus:outline-none focus:border-indigo-500 transition"
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
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[11px] border-b border-slate-200 font-semibold">
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
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    Loading orders...
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No orders matching your criteria.
                  </td>
                </tr>
              ) : (
                orders.map((o) => (
                  <tr
                    key={o.order_id}
                    className="hover:bg-slate-50/80 transition duration-150"
                  >
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-900">
                      {o.order_id}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-medium text-slate-900">{o.customer_name}</div>
                      <div className="text-[11px] text-slate-500">{o.email}</div>
                    </td>
                    <td className="py-3.5 px-4 max-w-xs truncate text-slate-700" title={o.product_title}>
                      {o.product_title}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-medium text-slate-900">
                      ${o.price_usd.toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4">{getStatusBadge(o.status)}</td>
                    <td className="py-3.5 px-4 text-slate-600">{o.expected_delivery}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 font-mono text-[11px] text-slate-700">
                        {o.carrier}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {onSelectOrderForChat && (
                        <button
                          onClick={() => onSelectOrderForChat(o.order_id)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-white hover:bg-indigo-50 text-indigo-700 border border-slate-300 hover:border-indigo-200 transition text-[11px] font-medium shadow-2xs"
                          title="Ask Copilot about this order"
                        >
                          <MessageSquare className="w-3 h-3 text-indigo-600" />
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
        <div className="flex items-center justify-between p-3.5 bg-slate-50/70 border-t border-slate-200 text-xs text-slate-500">
          <span>
            Showing rows {offset + 1} to {offset + orders.length}
          </span>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setOffset((prev) => Math.max(0, prev - limit))}
              disabled={offset === 0 || loading}
              className="p-1.5 rounded-md border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 transition text-slate-700"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setOffset((prev) => prev + limit)}
              disabled={orders.length < limit || loading}
              className="p-1.5 rounded-md border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 transition text-slate-700"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
