import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { App } from '../App';
import { Header } from '../components/Header';
import { ClassifierLab } from '../components/ClassifierLab';
import { EvaluationLab } from '../components/EvaluationLab';
import { ArchitectureGuide } from '../components/ArchitectureGuide';

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
    expect(screen.getByText(/SupportMind Copilot © 2026 NovaCart/i)).toBeDefined();
    expect(screen.getByText(/Prompt Strategy:/i)).toBeDefined();
    expect(screen.getByText(/V3/i)).toBeDefined();
  });

  it('switches navigation tab to System Design view', () => {
    render(<App />);
    const archButtons = screen.getAllByText('System Design');
    fireEvent.click(archButtons[0]);

    expect(screen.getByText(/System Design & Interview Portfolio Guide/i)).toBeDefined();
    expect(screen.getByText(/Min-Heap Top-K Retrieval DSA/i)).toBeDefined();
    expect(screen.getByText(/O\(1\) LRU Cache DSA/i)).toBeDefined();
  });

  it('switches navigation tab to Supervisor Queue view', () => {
    render(<App />);
    const queueButtons = screen.getAllByText('Supervisor Queue');
    fireEvent.click(queueButtons[0]);

    expect(screen.getByText(/Human-in-the-Loop Supervisor Queue/i)).toBeDefined();
  });

  it('renders ClassifierLab with quick test examples', () => {
    render(<ClassifierLab />);
    expect(screen.getByText(/Machine Learning Classifier Lab/i)).toBeDefined();
    expect(screen.getByText(/Double Billed \(Billing\)/i)).toBeDefined();
    expect(screen.getByText(/Late Delivery \(Delivery\)/i)).toBeDefined();
  });

  it('renders EvaluationLab with benchmark metrics', () => {
    render(<EvaluationLab />);
    expect(screen.getByText(/RAG & Prompt Evaluation Lab/i)).toBeDefined();
    expect(screen.getByText(/Compare Metric:/i)).toBeDefined();
    expect(screen.getAllByText(/Answer Correctness/i).length).toBeGreaterThanOrEqual(1);
  });

  it('renders ArchitectureGuide with resume bullet points', () => {
    render(<ArchitectureGuide />);
    expect(screen.getByText(/Resume Ready Bullet Points/i)).toBeDefined();
    expect(screen.getByText(/Technical Interview Q&A Deep Dive/i)).toBeDefined();
  });
});
