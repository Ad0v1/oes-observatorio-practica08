"""Ajusta la paginación de los .docx generados.

- Las filas de tabla no se parten entre páginas.
- La fila de encabezado se repite si la tabla continúa en otra página.
- Cada título queda unido al párrafo o tabla que lo sigue.
- Tablas cortas (<= 12 filas) se mantienen juntas en una sola página.

Uso: python ajustar_paginacion.py archivo1.docx [archivo2.docx ...]
"""
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _flag(tr_pr, tag):
    if tr_pr.find(qn(tag)) is None:
        tr_pr.append(OxmlElement(tag))


def ajustar(ruta: str) -> None:
    doc = Document(ruta)
    for p in doc.paragraphs:
        if p.style.name.startswith("Heading") or p.style.name == "Title":
            p.paragraph_format.keep_with_next = True
    for t in doc.tables:
        filas = t.rows
        for i, fila in enumerate(filas):
            tr_pr = fila._tr.get_or_add_trPr()
            _flag(tr_pr, "w:cantSplit")
            if i == 0:
                _flag(tr_pr, "w:tblHeader")
            if len(filas) <= 12 and i < len(filas) - 1:
                for celda in fila.cells:
                    for p in celda.paragraphs:
                        p.paragraph_format.keep_with_next = True
    doc.save(ruta)
    print("Ajustado:", ruta)


if __name__ == "__main__":
    for r in sys.argv[1:]:
        ajustar(r)
