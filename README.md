# Observatorio de Educación Superior (OES) — Prototipo académico

Práctica Guiada N.° 08 · Python + SQLite + Streamlit. Registra, clasifica, consulta y visualiza
novedades de educación superior peruana con trazabilidad de fuentes. Implementación educativa
original: no reproduce el código ni la identidad del OES comercial.

## Ejecutar en local (Windows)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate          # si PowerShell lo bloquea: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python -m pip install -r requirements.txt
python preparar_datos.py        # crea oes.db con los 3 registros DEMO (no duplica si se repite)
streamlit run app.py            # http://localhost:8501
```

## Registrar noticias reales verificadas

Revisar la nota original (URL directa, titular y fecha) y luego:

```powershell
python agregar_noticia.py --titulo "..." --institucion "SUNEDU" --categoria "Ente regulador" `
  --fuente "Plataforma gob.pe – SUNEDU" --fecha 2026-11-10 --url "https://..." `
  --resumen "Resumen propio" --tema "Calidad y licenciamiento" --verificado-por "Nombre del integrante"
python agregar_noticia.py --csv datos\noticias_univ.csv   # carga por lotes
```

La validación rechaza fechas inválidas o futuras, URLs de portada en noticias verificadas,
marcadores de ejemplo y URLs duplicadas. En la app, la pestaña **Registrar** exige la clave
`clave_registro` si está definida en los *secrets*; sin clave, solo funciona en `localhost`.

**Publicación en Streamlit Community Cloud:** la versión pública es de solo lectura. El disco
de la nube no es permanente: una noticia registrada desde la app se pierde al reiniciarse.
Las noticias se cargan en local, se sube `oes.db` actualizado al repositorio y la app se
actualiza sola.

## Pruebas

```powershell
python -m pytest tests -q       # P1–P6 de la guía + validaciones
```

## Estructura

| Archivo | Función |
|---|---|
| `oes_db.py` | Capa de datos: esquema, validación, inserción, filtros, CSV |
| `preparar_datos.py` | Crea la base y los 3 registros DEMO |
| `agregar_noticia.py` | Alta de noticias verificadas (campos o CSV) |
| `app.py` | Dashboard Streamlit |
| `tests/test_oes.py` | Pruebas automáticas |
| `datos/` | Noticias verificadas en CSV |
| `informe/` | Diagrama, capturas de evidencia e informe |
