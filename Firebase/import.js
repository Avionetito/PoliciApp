// import.js  ─ Node 20
import fs from "node:fs";
import { parse } from "csv-parse/sync";
import { initializeApp, cert } from "firebase-admin/app";
import { getFirestore, FieldValue, Timestamp } from "firebase-admin/firestore";

// ① arranca Firebase
initializeApp({ credential: cert(process.env.GOOGLE_APPLICATION_CREDENTIALS) });
const db = getFirestore();

// ② lee CSV
const csv = fs.readFileSync("../OCRPipeline/Output/questions.csv", "utf8");
const rows = parse(csv, { columns: true, skip_empty_lines: true });

// ③ transforma y escribe por lotes (≤500 writes/batch)
let batch = db.batch();
let writes = 0;

for (const r of rows) {
  const docId = `${r.tema}-${r.number}`;
  const docRef = db.collection("questions").doc(docId);

  batch.set(docRef, {
    tema: Number(r.tema),
    number: Number(r.number),
    text: r.text.trim(),
    options: {
      a: r.a.trim(),
      b: r.b.trim(),
      c: r.c.trim(),
      d: r.d.trim(),
    },
    answer: r.answer.trim().toLowerCase(),   // normaliza
    randomKey: Math.random(),
    createdAt: Timestamp.now(),              // opcional para auditoría
  });

  if (++writes === 500) {          // descarga batch
    await batch.commit();
    batch = db.batch();
    writes = 0;
  }
}
if (writes) await batch.commit();
console.log("✅  Importación completada");
