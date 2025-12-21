from __future__ import annotations

import argparse
from pathlib import Path


def extract_with_pymupdf(pdf_path: Path) -> str:
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "PyMuPDF (fitz) n'est pas installé. Installe-le avec: pip install pymupdf"
        ) from exc

    doc = fitz.open(pdf_path)
    chunks = []
    for i, page in enumerate(doc, start=1):
        chunks.append(f"===== PAGE {i} =====")
        chunks.append(page.get_text("text"))
    return "\n".join(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract plain text from a PDF with page markers")
    parser.add_argument("pdf")
    parser.add_argument("--out", default=None)

    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF introuvable: {pdf_path}")

    out_path = Path(args.out).expanduser().resolve() if args.out else pdf_path.with_suffix(".txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    text = extract_with_pymupdf(pdf_path)
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
