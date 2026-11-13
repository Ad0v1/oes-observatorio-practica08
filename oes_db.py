"""Capa de datos del Observatorio de Educación Superior (única que toca SQLite)."""
from __future__ import annotations

import os
import re
import sqlite3
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

CATEGORIAS = ("Ente rector", "Ente regulador", "Universidad pública", "Universidad privada")
TEMAS = ("Admisión y captación", "Becas y financiamiento", "Calidad y licenciamiento",
         "Investigación e innovación", "Imagen institucional y eventos",
         "Normativa y políticas", "Alianzas y convenios", "Sin tema")
ESTADOS = ("Ejemplo didáctico", "Verificada", "Pendiente")

COLUMNAS = ["id", "titulo", "institucion", "categoria", "fuente", "fecha", "url", "resumen",
            "tema", "estado_verificacion", "fecha_captura", "verificado_por"]

ESQUEMA = """
CREATE TABLE IF NOT EXISTS noticias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    institucion TEXT NOT NULL,
    categoria TEXT NOT NULL,
    fuente TEXT NOT NULL,
    fecha TEXT NOT NULL CHECK (fecha = date(fecha)),
    url TEXT NOT NULL UNIQUE,
    resumen TEXT NOT NULL,
    tema TEXT NOT NULL DEFAULT 'Sin tema',
    estado_verificacion TEXT NOT NULL DEFAULT 'Ejemplo didáctico'
        CHECK (estado_verificacion IN ('Ejemplo didáctico','Verificada','Pendiente')),
    fecha_captura TEXT NOT NULL DEFAULT (date('now','localtime')),
    verificado_por TEXT
);
"""

# Columnas nuevas que se agregan por ALTER TABLE si la base es antigua.
# (SQLite no admite DEFAULT no constante en ADD COLUMN, por eso fecha_captura usa un literal.)
_MIGRACION = {
    "tema": "TEXT NOT NULL DEFAULT 'Sin tema'",
    "estado_verificacion": "TEXT NOT NULL DEFAULT 'Ejemplo didáctico'",
    "fecha_captura": "TEXT NOT NULL DEFAULT '2026-11-06'",
    "verificado_por": "TEXT",
}


def _demo(titulo, inst, cat, fecha, url, resumen, tema) -> dict:
    return {"titulo": titulo, "institucion": inst, "categoria": cat,
            "fuente": "Portal institucional (ejemplo)", "fecha": fecha, "url": url,
            "resumen": resumen, "tema": tema, "estado_verificacion": "Ejemplo didáctico"}


DEMO: list[dict] = [
    _demo("Ejemplo: convocatoria de becas", "PRONABEC", "Ente rector", "2026-11-06",
          "https://www.pronabec.gob.pe/", "Registro didáctico: verificar nota original.",
          "Becas y financiamiento"),
    _demo("Ejemplo: actividad de investigación", "UNMSM", "Universidad pública", "2026-11-06",
          "https://www.unmsm.edu.pe/", "Registro didáctico: verificar noticia original.",
          "Investigación e innovación"),
    _demo("Ejemplo: programa académico", "PUCP", "Universidad privada", "2026-11-05",
          "https://www.pucp.edu.pe/", "Registro didáctico: verificar noticia original.",
          "Admisión y captación"),
]


def ruta_db() -> Path:
    """Ruta de la base: variable OES_DB si existe; si no, oes.db junto a este módulo."""
    valor = os.environ.get("OES_DB")
    return Path(valor) if valor else Path(__file__).with_name("oes.db")


def conectar(ruta: Path | None = None) -> sqlite3.Connection:
    """Abre una conexión SQLite (ruta por defecto: ruta_db())."""
    return sqlite3.connect(str(ruta if ruta is not None else ruta_db()))


def crear_esquema(con: sqlite3.Connection) -> None:
    """Crea la tabla y agrega las columnas nuevas si la base es de una versión anterior."""
    con.execute(ESQUEMA)
    existentes = {f[1] for f in con.execute("PRAGMA table_info(noticias)")}
    for col, definicion in _MIGRACION.items():
        if col not in existentes:
            con.execute(f"ALTER TABLE noticias ADD COLUMN {col} {definicion}")
    con.commit()


def insertar_demo(con: sqlite3.Connection) -> None:
    """Inserta los registros DEMO sin duplicar (INSERT OR IGNORE por URL única)."""
    for d in DEMO:
        con.execute(
            "INSERT OR IGNORE INTO noticias (titulo, institucion, categoria, fuente, fecha, url,"
            " resumen, tema, estado_verificacion) VALUES (?,?,?,?,?,?,?,?,?)",
            (d["titulo"], d["institucion"], d["categoria"], d["fuente"], d["fecha"], d["url"],
             d["resumen"], d["tema"], d["estado_verificacion"]))
    con.commit()


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", str(s)).upper()


def validar_noticia(d: dict) -> list[str]:
    """Devuelve la lista de errores (en español); vacía si la noticia es válida."""
    err: list[str] = []
    v = {k: str(d.get(k) or "").strip() for k in
         ("titulo", "institucion", "categoria", "fuente", "fecha", "url", "resumen",
          "tema", "estado_verificacion", "verificado_por")}
    tema = v["tema"] or "Sin tema"
    estado = v["estado_verificacion"] or "Pendiente"

    for campo in ("titulo", "institucion", "categoria", "fuente", "fecha", "url", "resumen"):
        if not v[campo]:
            err.append(f"El campo '{campo}' es obligatorio")

    # Fecha
    if v["fecha"]:
        try:
            f = datetime.strptime(v["fecha"], "%Y-%m-%d").date()
            if f > date.today():
                err.append("La fecha no puede ser futura")
        except ValueError:
            err.append("La fecha debe tener formato AAAA-MM-DD válido")

    # URL
    url = v["url"]
    if url:
        p = urlparse(url)
        if p.scheme not in ("http", "https") or not p.netloc or "." not in p.netloc:
            err.append("La URL debe empezar con http:// o https:// y tener dominio")
        if "URL-DIRECTA" in url.upper() or "EJEMPLO.COM" in url.upper():
            err.append("La URL es un marcador, no una URL real")

    # Marcadores de la guía
    marcadores = {"titulo": "TÍTULO VERIFICADO", "institucion": "INSTITUCIÓN",
                  "fuente": "FUENTE OFICIAL", "resumen": "RESUMEN REDACTADO Y VERIFICADO"}
    for campo, m in marcadores.items():
        if v[campo] and _norm(v[campo]) == _norm(m):
            err.append(f"El campo '{campo}' contiene un marcador sin reemplazar")

    if v["categoria"] and v["categoria"] not in CATEGORIAS:
        err.append("Categoría no permitida: " + v["categoria"])
    if tema not in TEMAS:
        err.append("Tema no permitido: " + tema)
    if estado not in ESTADOS:
        err.append("Estado de verificación no permitido: " + estado)

    if estado == "Verificada":
        if not v["verificado_por"]:
            err.append("Una noticia Verificada requiere 'verificado_por'")
        if url and urlparse(url).path in ("", "/"):
            err.append("Una noticia Verificada requiere URL directa (no la portada)")
    return err


def insertar_noticia(d: dict, ruta: Path | None = None) -> tuple[bool, str]:
    """Valida e inserta una noticia. Devuelve (éxito, mensaje)."""
    errores = validar_noticia(d)
    if errores:
        return False, "; ".join(errores)
    g = lambda k: str(d.get(k) or "").strip()
    con = conectar(ruta)
    try:
        crear_esquema(con)
        try:
            con.execute(
                "INSERT INTO noticias (titulo, institucion, categoria, fuente, fecha, url, resumen,"
                " tema, estado_verificacion, fecha_captura, verificado_por)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (g("titulo"), g("institucion"), g("categoria"), g("fuente"), g("fecha"), g("url"),
                 g("resumen"), g("tema") or "Sin tema", g("estado_verificacion") or "Pendiente",
                 g("fecha_captura") or date.today().isoformat(), g("verificado_por") or None))
            con.commit()
        except sqlite3.IntegrityError:
            return False, "Duplicada: ya existe una noticia con esa URL"
    finally:
        con.close()
    return True, "Noticia registrada"


def leer_noticias(ruta: Path | None = None) -> pd.DataFrame:
    """Lee todas las noticias, más recientes primero (DataFrame vacío con columnas si no hay)."""
    con = conectar(ruta)
    try:
        return pd.read_sql_query("SELECT * FROM noticias ORDER BY fecha DESC, id DESC", con)
    except (pd.errors.DatabaseError, sqlite3.Error):
        return pd.DataFrame(columns=COLUMNAS)
    finally:
        con.close()


def filtrar(df: pd.DataFrame, categorias=None, texto: str = "", estados=None,
            desde: date | None = None, hasta: date | None = None) -> pd.DataFrame:
    """Aplica filtros; None = sin filtro, lista vacía = 0 filas."""
    r = df
    if categorias is not None:
        r = r[r["categoria"].isin(list(categorias))]
    if estados is not None:
        r = r[r["estado_verificacion"].isin(list(estados))]
    if texto and texto.strip():
        t = texto.strip()
        m = (r["titulo"].str.contains(t, case=False, regex=False, na=False)
             | r["institucion"].str.contains(t, case=False, regex=False, na=False))
        r = r[m]
    if desde is not None:
        r = r[r["fecha"] >= desde.isoformat()]
    if hasta is not None:
        r = r[r["fecha"] <= hasta.isoformat()]
    return r


def a_csv(df: pd.DataFrame) -> bytes:
    """Serializa el DataFrame a CSV UTF-8 con BOM (compatible con Excel)."""
    copia = df.copy()
    peligrosos = ("=", "+", "-", "@", "\t", "\r")
    for col in copia.columns:
        if not pd.api.types.is_numeric_dtype(copia[col]):
            copia[col] = copia[col].map(
                lambda v: "'" + v if isinstance(v, str) and v.startswith(peligrosos) else v)
    return copia.to_csv(index=False).encode("utf-8-sig")
