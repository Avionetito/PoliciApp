#!/usr/bin/env python3
# Requires: pip install pdf2image pytesseract pillow opencv-python tqdm jsonlines


# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\.venv\Scripts\activate.ps1


from pathlib import Path
import re, csv, jsonlines, pytesseract, cv2, logging, numpy as np
from pdf2image import convert_from_path
from dataclasses import dataclass, asdict
from tqdm import tqdm
from PIL import Image, ImageOps

# ---------- Config ----------
SRC_DIR       = Path("../Data")          # PDFs originales
CACHE_DIR     = Path(".cache")           # Texto OCR por página
OUT_DIR       = Path("Output")           # JSONL / CSV
DPI           = 200                      # reduce tamaño pero mantiene precisión
TESS_CONFIG   = "--oem 3 --psm 4 -l spa" # español
OUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# ---------- Logging ----------
logging.basicConfig(
    filename="ocr.log",
    level=logging.INFO,
    format="%(levelname)s | %(pdf)s p%(page)02d | %(message)s",
)
log = logging.getLogger(__name__)

# ---------- Dataclass ----------
@dataclass
class Question:
    tema: str
    number: int
    text: str
    options: list[str]      # a, b, c, d
    answer: str             # "a" | "b" | "c" | "d"

# ---------- OCR prep ----------
def preprocess(pil_img: Image.Image) -> np.ndarray:
    # Convertir a gris, autocontrast y binarizar (Otsu)
    gray = ImageOps.autocontrast(pil_img.convert("L"))
    arr  = np.array(gray)
    if arr.shape[0] > 3500:       # escala ↓ si la página es enorme
        scale = 3500 / arr.shape[0]
        arr   = cv2.resize(arr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    _, th = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th

# ---------- Parsing ----------
Q_REGEX = re.compile(
    r"""                # ejemplo: 12. Texto ...  a) ... b) ... c) ... d) ... Respuesta correcta: a
    (?P<num>\d{1,3})\s* [\.\)\-]\s*      # número + separador
    (?P<q>.+?)             # cuerpo de la pregunta (lazy)
    \s+a\)\s*(?P<a>.+?)    # opción a
    \s+b\)\s*(?P<b>.+?)    # opción b
    \s+c\)\s*(?P<c>.+?)    # opción c
    \s+d\)\s*(?P<d>.+?)    # opción d
    \s*Respuesta\s+correcta:\s*(?P<ans>[abcd]) # solución
    """,
    flags=re.IGNORECASE | re.DOTALL | re.VERBOSE,
)

def parse_questions(raw: str, tema: str) -> list[Question]:
    txt = re.sub(r"\s+", " ", raw.strip())  # normaliza espacios
    qs  = []
    for m in Q_REGEX.finditer(txt):
        qs.append(
            Question(
                tema=tema,
                number=int(m["num"]),
                text=m["q"].strip(),
                options=[m["a"].strip(), m["b"].strip(), m["c"].strip(), m["d"].strip()],
                answer=m["ans"].lower(),
            )
        )
    return qs

# ---------- Procesar PDF ----------
def process_pdf(pdf_path: Path) -> list[Question]:
    tema     = pdf_path.stem.split()[1]  # «Tema 36 Test.pdf» → “36”
    pdf_cache = CACHE_DIR / pdf_path.stem
    pdf_cache.mkdir(exist_ok=True)

    questions = []
    pages = convert_from_path(pdf_path, dpi=DPI)
    for idx, img in enumerate(pages, 1):
        cache_txt = pdf_cache / f"page_{idx:03d}.txt"

        if cache_txt.exists():
            raw = cache_txt.read_text(encoding="utf-8")
        else:
            th  = preprocess(img)
            raw = pytesseract.image_to_string(th, config=TESS_CONFIG)
            cache_txt.write_text(raw, encoding="utf-8")

        page_qs = parse_questions(raw, tema)
        if page_qs:
            log.info(f"{len(page_qs)} preguntas extraídas", extra={"pdf": pdf_path.name, "page": idx})
            questions.extend(page_qs)
        else:
            log.warning("sin coincidencias", extra={"pdf": pdf_path.name, "page": idx})

    return questions

# ---------- Main ----------
def main() -> None:
    pdfs = list(SRC_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No hay PDFs en {SRC_DIR.resolve()}")
        return

    all_qs: list[Question] = []
    for pdf in tqdm(pdfs, desc="PDFs"):
        all_qs.extend(process_pdf(pdf))

    # ---- Guardar ----
    json_path = OUT_DIR / "questions.jsonl"
    csv_path  = OUT_DIR / "questions.csv"

    with jsonlines.open(json_path, mode="w") as w:
        w.write_all(asdict(q) for q in all_qs)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tema", "number", "text", "a", "b", "c", "d", "answer"])
        for q in all_qs:
            w.writerow([q.tema, q.number, q.text, *q.options, q.answer])

    print(f"✅ {len(all_qs)} preguntas guardadas → {json_path.relative_to(Path.cwd())}")

if __name__ == "__main__":
    main()