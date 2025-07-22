'use client';
import TopicPicker from '@/components/TopicPicker';
import { ExamProvider } from '@/lib/useExamStore';

export default function Home() {
  return (
    <ExamProvider>
      <main className="flex flex-col items-center gap-6 p-8">
        <h1 className="text-3xl font-bold">Tests Policía Nacional</h1>
        <TopicPicker />
      </main>
    </ExamProvider>
  );
}
