import { useState, useEffect } from 'react';
import { Header, type TabType } from './components/Header';
import { ChatWorkspace } from './components/ChatWorkspace';
import { ApprovalsQueue } from './components/ApprovalsQueue';
import { OrdersTable } from './components/OrdersTable';
import { ClassifierLab } from './components/ClassifierLab';
import { EvaluationLab } from './components/EvaluationLab';
import { fetchHealth, fetchPendingActions } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(true);

  const refreshPendingCount = async () => {
    try {
      const actions = await fetchPendingActions();
      const count = actions.filter((a) => a.status === 'pending_approval').length;
      setPendingCount(count);
    } catch {
      // fallback
    }
  };

  const checkHealth = async () => {
    try {
      const h = await fetchHealth();
      setIsBackendHealthy(h.status.includes('healthy'));
    } catch {
      setIsBackendHealthy(false);
    }
  };

  useEffect(() => {
    checkHealth();
    refreshPendingCount();

    const interval = setInterval(() => {
      refreshPendingCount();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const handleOrderTrackInChat = (orderId: string) => {
    setActiveTab('chat');
    setTimeout(() => {
      const input = document.querySelector('input[type="text"]') as HTMLInputElement;
      if (input) {
        input.value = `Can you check the delivery status of order ${orderId}?`;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.focus();
      }
    }, 100);
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA] text-slate-900 flex flex-col font-sans">
      {/* Top Navbar */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        pendingActionsCount={pendingCount}
        isBackendHealthy={isBackendHealthy}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col">
        {activeTab === 'chat' && (
          <ChatWorkspace
            onOrderClick={handleOrderTrackInChat}
            onActionUpdated={refreshPendingCount}
          />
        )}
        {activeTab === 'approvals' && (
          <ApprovalsQueue onActionResolved={refreshPendingCount} />
        )}
        {activeTab === 'orders' && (
          <OrdersTable onSelectOrderForChat={handleOrderTrackInChat} />
        )}
        {activeTab === 'classifier' && <ClassifierLab />}
        {activeTab === 'eval' && <EvaluationLab />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            SupportMind © 2026 NovaCart Operations. Enterprise Support Copilot with Grounded Hybrid RAG.
          </span>
          <div className="flex items-center gap-3 text-slate-400">
            <span>FastAPI Backend</span>
            <span>•</span>
            <span>React + Vite + Tailwind</span>
            <span>•</span>
            <span>Scikit-Learn ML</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
