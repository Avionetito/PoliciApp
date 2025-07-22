'use client'; 
import { createContext, useContext, useEffect, useState } from 'react';

export type Question = {
  id: string;
  tema: number;
  texto: string;
  opciones: [string, string, string, string];
  correcta: 'a' | 'b' | 'c' | 'd';
};

type ExamState = {
  questions: Question[];
  answers: Record<string, Question['correcta'] | null>;
  startedAt: number;
};

type ExamStore = {
  state: ExamState | null;
  startExam: (qs: Question[]) => void;
  answer: (id: string, opt: Question['correcta']) => void;
  reset: () => void;
};

const ExamCtx = createContext<ExamStore | null>(null);

export const ExamProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, setState] = useState<ExamState | null>(null);
  const LS_KEY = 'police-exam-state';

  /* ---------- load from localStorage ---------- */
  useEffect(() => {
    const saved = localStorage.getItem(LS_KEY);
    if (saved) setState(JSON.parse(saved));
  }, []);

  /* ---------- save to localStorage ---------- */
  useEffect(() => {
    if (state) localStorage.setItem(LS_KEY, JSON.stringify(state));
    else localStorage.removeItem(LS_KEY);
  }, [state]);

  /* ---------- API ---------- */
  const startExam = (qs: Question[]) =>
    setState({
      questions: qs,
      answers: Object.fromEntries(qs.map((q) => [q.id, null])),
      startedAt: Date.now(),
    });

  const answer = (id: string, opt: Question['correcta']) =>
    setState((prev) =>
      prev ? { ...prev, answers: { ...prev.answers, [id]: opt } } : prev,
    );

  const reset = () => setState(null);

  return (
    <ExamCtx.Provider value={{ state, startExam, answer, reset }}>
      {children}
    </ExamCtx.Provider>
  );
};

export const useExamStore = () => {
  const ctx = useContext(ExamCtx);
  if (!ctx) throw new Error('Wrap tree in <ExamProvider>');
  return ctx;
};
