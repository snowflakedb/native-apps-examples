'use client';

import { ThemeToggle } from '@/components/theme-toggle';
import { Button } from '@/components/ui/button';
import { ArrowUp, Braces, CheckCircle2, Database, LoaderCircle, Sparkles } from 'lucide-react';
import { FormEvent, useState } from 'react';

type Analysis = {
  answer: string;
  sql: string;
  columns: string[];
  rows: Record<string, unknown>[];
  rowCount: number;
  source: string;
  freshness: string;
};

const suggestions = [
  'Which warehouses had the most queued time in the last 7 days?',
  'Show failed queries by error code over the past 24 hours.',
  'Which users drove the most execution time this month?',
];

function display(value: unknown) {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

export function Whisperer() {
  const [question, setQuestion] = useState('');
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState('');
  const [pending, setPending] = useState(false);
  const [showSql, setShowSql] = useState(false);

  async function submit(event?: FormEvent) {
    event?.preventDefault();
    if (!question.trim() || pending) return;
    setPending(true);
    setError('');
    setAnalysis(null);
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error ?? 'Analysis failed.');
      setAnalysis(body);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Analysis failed.');
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="min-h-screen overflow-hidden">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-6 sm:px-8">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-full bg-primary text-primary-foreground"><Sparkles size={17} /></div>
          <div><p className="font-display text-lg font-semibold leading-none">Warehouse Whisperer</p><p className="mt-1 text-xs text-muted-foreground">Query operations analyst</p></div>
        </div>
        <ThemeToggle />
      </header>

      <section className="query-grid relative border-y border-border/70 px-5 py-14 sm:px-8 sm:py-20">
        <div className="relative mx-auto max-w-4xl text-center">
          <p className="mb-4 text-sm font-medium text-primary">Ask your query history</p>
          <h1 className="font-display text-4xl font-semibold tracking-[-0.04em] sm:text-6xl">Turn warehouse noise into evidence.</h1>
          <p className="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg">Investigate spend, latency, failures, and workload behavior with governed SQL executed as you.</p>

          <form onSubmit={submit} className="mx-auto mt-10 max-w-3xl text-left">
            <label htmlFor="question" className="sr-only">Question about query activity</label>
            <div className="flex items-end gap-2 rounded-2xl border bg-card p-2 shadow-[0_20px_70px_-35px_rgba(0,0,0,.6)] focus-within:ring-2 focus-within:ring-ring">
              <textarea id="question" rows={2} maxLength={1000} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What changed in warehouse performance this week?" className="min-h-16 flex-1 resize-none bg-transparent px-3 py-2 text-base outline-none placeholder:text-muted-foreground" />
              <Button aria-label="Analyze query history" size="icon" type="submit" disabled={!question.trim() || pending} className="mb-1 rounded-full">{pending ? <LoaderCircle className="animate-spin" /> : <ArrowUp />}</Button>
            </div>
          </form>

          {!analysis && !pending && !error && <div className="mt-5 flex flex-wrap justify-center gap-2">{suggestions.map((item) => <button key={item} onClick={() => setQuestion(item)} className="rounded-full border bg-background/80 px-3 py-2 text-xs text-muted-foreground transition hover:border-primary hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring">{item}</button>)}</div>}
          {pending && <div className="mt-8 flex items-center justify-center gap-3 text-sm text-muted-foreground"><span className="analysis-pulse h-2.5 w-2.5 rounded-full bg-primary" />Reading query history and checking the evidence...</div>}
          {error && <div role="alert" className="mx-auto mt-8 max-w-2xl rounded-xl border border-destructive/40 bg-destructive/10 p-4 text-left text-sm text-destructive">{error}</div>}
        </div>
      </section>

      {analysis && <section className="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
        <div className="animate-rise grid gap-8 lg:grid-cols-[minmax(0,1.35fr)_minmax(260px,.65fr)]">
          <article>
            <div className="mb-4 flex items-center gap-2 text-sm font-medium text-primary"><CheckCircle2 size={16} />Grounded answer</div>
            <p className="font-display whitespace-pre-wrap text-2xl leading-relaxed tracking-tight sm:text-3xl">{analysis.answer}</p>
          </article>
          <aside className="border-l-2 border-primary/40 pl-5 text-sm">
            <p className="font-medium">Evidence contract</p>
            <p className="mt-3 flex gap-2 text-muted-foreground"><Database className="mt-0.5 shrink-0" size={15} />{analysis.source}</p>
            <p className="mt-2 text-muted-foreground">{analysis.freshness}</p>
            <p className="mt-2 text-muted-foreground">{analysis.rowCount} rows returned, maximum 200</p>
            <button onClick={() => setShowSql(!showSql)} className="mt-5 flex items-center gap-2 font-medium text-primary hover:underline"><Braces size={15} />{showSql ? 'Hide' : 'Inspect'} governed SQL</button>
          </aside>
        </div>

        {showSql && <pre className="mt-8 overflow-x-auto rounded-xl bg-[#111914] p-5 text-sm leading-relaxed text-[#c7f5d8]"><code>{analysis.sql}</code></pre>}

        {analysis.rows.length > 0 && <div className="mt-10 overflow-hidden border-y">
          <div className="overflow-x-auto"><table className="w-full min-w-max text-left text-sm"><thead><tr>{analysis.columns.map((column) => <th key={column} className="border-b bg-muted/50 px-4 py-3 font-medium">{column.replaceAll('_', ' ')}</th>)}</tr></thead><tbody>{analysis.rows.map((row, index) => <tr key={index} className="border-b last:border-0 hover:bg-muted/30">{analysis.columns.map((column) => <td key={column} className="max-w-80 truncate px-4 py-3 font-mono text-xs">{display(row[column])}</td>)}</tr>)}</tbody></table></div>
        </div>}
      </section>}

      <footer className="mx-auto flex max-w-7xl items-center justify-between px-5 py-8 text-xs text-muted-foreground sm:px-8"><span>Caller&apos;s rights · SELECT only · 90-day maximum</span><span>ACCOUNT_USAGE · UTC</span></footer>
    </main>
  );
}
