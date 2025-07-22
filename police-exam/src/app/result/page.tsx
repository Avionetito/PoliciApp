'use client';
import { useExamStore } from '@/lib/useExamStore';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ResultPage() {
  const { state, reset } = useExamStore();
  const router = useRouter();

  useEffect(() => {
    if (!state) router.replace('/');
  }, [state, router]);

  if (!state) return null;

  const total = state.questions.length;
  const correct = state.questions.filter(
    (q) => state.answers[q.id] === q.correcta,
  ).length;

  return (
    <main className="mx-auto flex max-w-md flex-col items-center gap-6 p-8">
      <h2 className="text-2xl font-bold">{`Resultado: ${correct} / ${total}`}</h2>
      <button
        className="rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white"
        onClick={() => {
          reset();
          router.push('/');
        }}
      >
        Nuevo test
      </button>
    </main>
  );
}
