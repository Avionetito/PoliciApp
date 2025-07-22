#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR pipeline para tests tipo-test de Policía.
  • Extrae preguntas (sin respuesta) de las páginas normales
  • Extrae las soluciones de la(s) página(s) finales
  • Funde ambos en un único JSONL / CSV
  • Cachea el OCR por página en .cache/  → re-ejecuciones mucho + rápidas
"""
from __future__ import annotations

from pathlib import Path
import re, csv, logging, jsonlines
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List

import numpy as np
import pytesseract, cv2
from pdf2image import convert_from_path
from PIL import Image, ImageOps
from tqdm import tqdm

# ────────────────────────────── Config ─────────────────────────────

SRC_DIR     = Path("../Data")      # PDFs de entrada
CACHE_DIR   = Path(".cache")
OUT_DIR     = Path("Output")
DPI         = 200                  # 200 = suficiente precisión, RAM contenida
TESS_CONFIG = "--oem 3 --psm 4 -l spa"

for d in (CACHE_DIR, OUT_DIR):
    d.mkdir(exist_ok=True)

logging.basicConfig(
    filename="ocr.log",
    level=logging.INFO,
    format="%(levelname)s | %(pdf)s p%(page)02d | %(message)s",
)
log = logging.getLogger(__name__)

# ────────────────────────────── Modelo ─────────────────────────────

@dataclass
class Question:
    tema: str
    number: int
    text: str
    options: List[str]              # [a, b, c, d]
    answer: Optional[str] = None    # se completará al final

# ────────────────────── Pre-proceso imagen (sin cambios) ───────────

def preprocess(pil_img: Image.Image) -> np.ndarray:
    gray = ImageOps.autocontrast(pil_img.convert("L"))
    arr  = np.array(gray)
    if arr.shape[0] > 3500:
        scale = 3500 / arr.shape[0]
        arr   = cv2.resize(arr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    _, th = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th

# ───────────────────── Regex de preguntas  (SIN “Respuesta correcta”) ──────────
Q_REGEX = re.compile(
    r"""
    (?P<num>\d{1,3})\s*[\.\-\)]\s*                 # 1-  /  1.  /  1)
    (?P<q>.+?)\s+a\)\s*(?P<a>.+?)\s+b\)\s*(?P<b>.+?)
    \s+c\)\s*(?P<c>.+?)\s+d\)\s*(?P<d>.+?)
    (?=\s+\d{1,3}\s*[\.\-\)]|$)                   # look-ahead: siguiente nº o fin
    """,
    re.IGNORECASE | re.DOTALL | re.VERBOSE,
)

# ───────── Regex de soluciones “nº: Letra”  (acepta ruido tipo “25:B_”) ───────
ANS_REGEX = re.compile(r"(\d{1,3})\s*[:\-]\s*([ABCDabcd])")

def parse_questions(raw: str, tema: str) -> List[Question]:
    clean = re.sub(r"\s+", " ", raw.strip())
    return [
        Question(
            tema=tema,
            number=int(m["num"]),
            text=m["q"].strip(),
            options=[m["a"].strip(), m["b"].strip(), m["c"].strip(), m["d"].strip()],
        )
        for m in Q_REGEX.finditer(clean)
    ]

def parse_answers(raw: str) -> Dict[int, str]:
    return {int(n): l.lower() for n, l in ANS_REGEX.findall(raw)}

# ───────────────────────── Procesar un PDF ────────────────────────

def process_pdf(pdf_path: Path) -> List[Question]:
    tema = pdf_path.stem.split()[1]       # «Tema 36 Test.pdf» → “36”
    q_by_num: Dict[int, Question] = {}
    answers: Dict[int, str] = {}

    pages = convert_from_path(pdf_path, dpi=DPI)
    pdf_cache = CACHE_DIR / pdf_path.stem
    pdf_cache.mkdir(exist_ok=True)

    for idx, img in enumerate(pages, 1):
        cache_txt = pdf_cache / f"page_{idx:03d}.txt"

        if cache_txt.exists():
            raw = cache_txt.read_text(encoding="utf-8")
        else:
            raw = pytesseract.image_to_string(preprocess(img), config=TESS_CONFIG)
            cache_txt.write_text(raw, encoding="utf-8")

        low = raw.lower()
        if "solucion" in low:      # página de respuestas
            new = parse_answers(raw)
            answers.update(new)
            log.info(f"{len(new)} soluciones", extra={"pdf": pdf_path.name, "page": idx})
        else:                      # página de preguntas
            qs = parse_questions(raw, tema)
            for q in qs:
                q_by_num[q.number] = q
            log.info(f"{len(qs)} preguntas", extra={"pdf": pdf_path.name, "page": idx})

    # --------- fusionar --------
    for num, ans in answers.items():
        if num in q_by_num:
            q_by_num[num].answer = ans
        else:
            log.warning(f"respuesta sin pregunta (nº {num})", extra={"pdf": pdf_path.name, "page": 0})

    return list(q_by_num.values())

# ────────────────────────── Main ──────────────────────────

def main() -> None:
    pdfs = sorted(SRC_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No hay PDFs en {SRC_DIR.resolve()}")
        return

    all_qs: List[Question] = []
    for pdf in tqdm(pdfs, desc="PDFs"):
        all_qs.extend(process_pdf(pdf))

    # guardar
    json_path = OUT_DIR / "questions.jsonl"
    csv_path  = OUT_DIR / "questions.csv"

    with jsonlines.open(json_path, "w") as w:
        w.write_all(asdict(q) for q in all_qs)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["tema", "number", "text", "a", "b", "c", "d", "answer"])
        for q in all_qs:
            wr.writerow([q.tema, q.number, q.text, *q.options, q.answer or ""])

    print(f"✅ {len(all_qs)} preguntas guardadas en {json_path.resolve()}")
    faltan = [q.number for q in all_qs if q.answer is None]
    if faltan:
        print(f"⚠️  Sin respuesta (probable OCR en SOLUCIONES): {faltan}")

if __name__ == "__main__":
    main()
