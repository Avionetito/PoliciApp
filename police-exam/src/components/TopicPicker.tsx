'use client';
import { useRouter } from 'next/navigation';
import { sample } from '@/lib/sampleData';
import { useExamStore } from '@/lib/useExamStore';

export default function TopicPicker() {
  const { startExam } = useExamStore();
  const router = useRouter();
  const temas = [...new Set(sample.map((q) => q.tema))];

  const handleStart = (tema: number) => {
    const qs = sample.filter((q) => q.tema === tema);
    startExam(qs);
    router.push('/exam');
  };

  return (
    <ul className="grid grid-cols-2 gap-4">
      {temas.map((t) => (
        <li key={t}>
          <button
            className="w-full rounded-xl border p-4 shadow-sm hover:bg-indigo-50"
            onClick={() => handleStart(t)}
          >
            Tema {t}
          </button>
        </li>
      ))}
    </ul>
  );
}
