'use client';
import { Question } from '@/lib/useExamStore';

type Props = {
  question: Question;
  selected: 'a' | 'b' | 'c' | 'd' | null;
  onSelect: (opt: 'a' | 'b' | 'c' | 'd') => void;
};

export default function QuestionCard({ question, selected, onSelect }: Props) {
  const labels = ['a', 'b', 'c', 'd'] as const;

  return (
    <article className="space-y-4 rounded-xl border p-6 shadow">
      <p className="font-medium">{question.texto}</p>
      {labels.map((l, i) => (
        <label
          key={l}
          className={`flex cursor-pointer items-center gap-3 rounded-lg p-2 ${
            selected === l ? 'bg-indigo-100' : 'hover:bg-gray-100'
          }`}
        >
          <input
            type="radio"
            name={question.id}
            className="accent-indigo-600"
            checked={selected === l}
            onChange={() => onSelect(l)}
          />
          <span>{question.opciones[i]}</span>
        </label>
      ))}
    </article>
  );
}
