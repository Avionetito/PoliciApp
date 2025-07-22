'use client';
import { useExamStore } from '@/lib/useExamStore';
import QuestionCard from '@/components/QuestionCard';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ExamPage() {
  const { state, answer } = useExamStore();
  const router = useRouter();
  const [index, setIndex] = useState(0);

  // If user hit /exam directly without starting, bounce back.
  useEffect(() => {
    if (state === null) router.replace('/');
  }, [state, router]);

  // While we’re waiting for provider hydration, show nothing.
  if (state === null) return null;

  const q = state.questions[index];
  const userChoice = state.answers[q.id];

  const handleNext = () => {
    if (index === state.questions.length - 1) router.push('/result');
    else setIndex(index + 1);
  };

  return (
    <main className="mx-auto max-w-xl p-6">
      <QuestionCard
        question={q}
        selected={userChoice}
        onSelect={(opt) => answer(q.id, opt)}
      />
      <button
        className="mt-6 w-full rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white disabled:opacity-40"
        disabled={userChoice === null}
        onClick={handleNext}
      >
        {index === state.questions.length - 1 ? 'Finalizar' : 'Siguiente'}
      </button>
    </main>
  );
}
