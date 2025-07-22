'use client';                 // ← this file runs only in the browser

import { ExamProvider } from '@/lib/useExamStore';

export function Providers({ children }: { children: React.ReactNode }) {
  return <ExamProvider>{children}</ExamProvider>;
}
