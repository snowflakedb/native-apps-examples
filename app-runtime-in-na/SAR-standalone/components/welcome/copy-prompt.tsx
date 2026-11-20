'use client';

// Example prompt with a copy button, for the welcome page. Delete with it.

import { copyText } from '@/lib/clipboard';
import { Check, Copy } from 'lucide-react';
import { useState } from 'react';

export function CopyPrompt({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  return (
    <div className="mt-3 flex items-start gap-2 rounded-md border bg-muted/60 p-3">
      <p className="min-w-0 flex-1 text-sm leading-relaxed">{text}</p>
      <button
        type="button"
        aria-label={copied ? 'Copied' : 'Copy prompt'}
        className="shrink-0 rounded p-1 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        onClick={async () => {
          // Show "copied" only when the copy worked; Snowsight's iframe can block it.
          if (await copyText(text)) {
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
          }
        }}
      >
        {copied ? <Check className="h-4 w-4 text-success" /> : <Copy className="h-4 w-4" />}
      </button>
    </div>
  );
}
