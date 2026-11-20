'use client';

import { useTheme } from '@/components/theme-provider';
import { Button } from '@/components/ui/button';
import { Monitor, Moon, Sun } from 'lucide-react';

// Cycles system → light → dark. "System" follows the OS setting, and is the default.
const NEXT = { system: 'light', light: 'dark', dark: 'system' } as const;
const LABEL = { system: 'System theme', light: 'Light theme', dark: 'Dark theme' } as const;
const ICON = { system: Monitor, light: Sun, dark: Moon } as const;

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const Icon = ICON[theme];

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={`${LABEL[theme]}. Switch to ${LABEL[NEXT[theme]].toLowerCase()}`}
      title={`${LABEL[theme]} (click for ${LABEL[NEXT[theme]].toLowerCase()})`}
      onClick={() => setTheme(NEXT[theme])}
    >
      <Icon className="h-4 w-4" />
    </Button>
  );
}
