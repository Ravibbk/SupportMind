import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { App } from '../App';
import { Header } from '../components/Header';
import { ClassifierLab } from '../components/ClassifierLab';
import { EvaluationLab } from '../components/EvaluationLab';
import { OrdersTable } from '../components/OrdersTable';

// Mock scrollIntoView for jsdom
window.HTMLElement.prototype.scrollIntoView = vi.fn();

// Mock fetch for API calls in tests
globalThis.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve([]),
  } as unknown as Response)
);

describe('SupportMind Frontend Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders Header with branding and navigation tabs', () => {
    const onTabChange = vi.fn();
    render(
      <Header
        activeTab="chat"
        onTabChange={onTabChange}
        pendingActionsCount={3}
        isBackendHealthy={true}
      />
    );

    expect(screen.getByText('SupportMind')).toBeDefined();
    expect(screen.getByText('NovaCart Copilot')).toBeDefined();
    expect(screen.getAllByText('Copilot Chat').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Supervisor Queue').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('3').length).toBeGreaterThanOrEqual(1); // pending badge count
  });

  it('renders App and defaults to Copilot Chat view', () => {
    render(<App />);
    expect(screen.getByText(/SupportMind © 2026 NovaCart Operations/i)).toBeDefined();
    expect(screen.getByText(/Prompt Strategy:/i)).toBeDefined();
    expect(screen.getByText(/V3/i)).toBeDefined();
  });

  it('switches navigation tab to Fulfillment Orders view', () => {
    render(<App />);
    const ordersButtons = screen.getAllByText('Fulfillment Orders');
    fireEvent.click(ordersButtons[0]);

    expect(screen.getAllByText(/Fulfillment Orders/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/500 Orders/i)).toBeDefined();
  });

  it('switches navigation tab to Supervisor Queue view', () => {
    render(<App />);
    const queueButtons = screen.getAllByText('Supervisor Queue');
    fireEvent.click(queueButtons[0]);

    expect(screen.getByText(/Supervisor Approvals Queue/i)).toBeDefined();
  });

  it('renders ClassifierLab with quick test examples', () => {
    render(<ClassifierLab />);
    expect(screen.getByText(/Machine Learning Classifier Lab/i)).toBeDefined();
    expect(screen.getByText(/Double Billed \(Billing\):/i)).toBeDefined();
    expect(screen.getByText(/Late Delivery \(Delivery\):/i)).toBeDefined();
  });

  it('renders EvaluationLab with benchmark metrics', () => {
    render(<EvaluationLab />);
    expect(screen.getByText(/RAG & Retrieval Evaluation Lab/i)).toBeDefined();
    expect(screen.getByText(/Compare Metric:/i)).toBeDefined();
    expect(screen.getAllByText(/Answer Correctness/i).length).toBeGreaterThanOrEqual(1);
  });

  it('renders OrdersTable with search and filters', () => {
    render(<OrdersTable />);
    expect(screen.getAllByText(/Fulfillment Orders/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/All Statuses/i)).toBeDefined();
  });
});
