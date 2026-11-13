"""Registra noticias en la base: desde un CSV (--csv) o campos sueltos."""
import argparse
import csv
import sys

import oes_db


def cargar_csv(ruta_csv: str) -> int:
    """Carga un CSV (cabecera del contrato); ignora 'evidencia'. Devuelve código de salida."""
    reg = dup = rech = 0
    with open(ruta_csv, newline="", encoding="utf-8-sig") as f:
        for n, fila in enumerate(csv.DictReader(f), start=2):  # línea 1 = cabecera
            d = {k: (fila.get(k) or "").strip() for k in
                 ("titulo", "institucion", "categoria", "fuente", "fecha", "url",
                  "resumen", "tema", "verificado_por")}
            d["estado_verificacion"] = "Verificada"
            ok, msg = oes_db.insertar_noticia(d, oes_db.ruta_db())
            if ok:
                reg += 1
                estado = "REGISTRADA"
            elif msg.startswith("Duplicada"):
                dup += 1
                estado = "DUPLICADA"
            else:
                rech += 1
                estado = "RECHAZADA"
            print(f"Fila {n} [{estado}] {d['titulo'][:60]} — {msg}")
    print(f"Resumen: {reg} registradas, {dup} duplicadas, {rech} rechazadas")
    return 0 if rech == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Agrega noticias al Observatorio (OES).")
    p.add_argument("--csv", help="Ruta de un CSV con la cabecera del contrato")
    for campo in ("titulo", "institucion", "categoria", "fuente", "fecha", "url", "resumen", "tema"):
        p.add_argument(f"--{campo}")
    p.add_argument("--verificado-por", dest="verificado_por")
    a = p.parse_args()

    if a.csv:
        return cargar_csv(a.csv)

    d = {k: getattr(a, k) or "" for k in
         ("titulo", "institucion", "categoria", "fuente", "fecha", "url", "resumen", "tema")}
    d["verificado_por"] = a.verificado_por or ""
    d["estado_verificacion"] = "Verificada" if a.verificado_por else "Pendiente"
    ok, msg = oes_db.insertar_noticia(d, oes_db.ruta_db())
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
