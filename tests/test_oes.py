"""Pruebas del OES (P0-P6 de la guía + validaciones). Se escriben contra coordinacion/contrato.md."""
import subprocess
import sys
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
APP = str(RAIZ / "app.py")
PREPARAR = str(RAIZ / "preparar_datos.py")
sys.path.insert(0, str(RAIZ))


def preparar(env_db, entorno):
    return subprocess.run([sys.executable, PREPARAR], env=entorno, cwd=str(RAIZ),
                          capture_output=True, text=True, timeout=60)


@pytest.fixture
def db(tmp_path, monkeypatch):
    ruta = tmp_path / "oes_test.db"
    monkeypatch.setenv("OES_DB", str(ruta))
    import os
    r = preparar(ruta, os.environ.copy())
    assert r.returncode == 0, r.stdout + r.stderr
    import oes_db
    return oes_db, ruta


def nueva(**kw):
    d = dict(titulo="Nota verificada de prueba", institucion="MINEDU", categoria="Ente rector",
             fuente="gob.pe", fecha="2026-11-10", url="https://www.gob.pe/institucion/minedu/noticias/12345-nota-prueba",
             resumen="Resumen propio de prueba.", tema="Normativa y políticas",
             estado_verificacion="Verificada", verificado_por="Agente A5 (IA)")
    d.update(kw)
    return d


def app():
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    return at


def metricas(at):
    return {m.label: m.value for m in at.metric}


def tabla(at):
    # dataframe[0] es la matriz institución x tema (Panorama); la tabla de noticias es la que tiene 'url'.
    for d in at.dataframe:
        if "url" in d.value.columns:
            return d.value
    raise AssertionError("tabla de noticias no encontrada")


def test_p1_idempotencia(db):
    oes_db, ruta = db
    import os
    r = preparar(ruta, os.environ.copy())
    assert r.returncode == 0, r.stdout + r.stderr
    df = oes_db.leer_noticias()
    assert len(df) == 3
    assert df["url"].is_unique


def test_p0_metricas_sin_filtros(db):
    at = app()
    assert not at.exception
    m = metricas(at)
    assert m["Noticias"] == "3"
    assert m["Instituciones"] == "3"
    assert m["Categorías"] == "3"


def test_p2_filtro_categoria(db):
    at = app()
    at.multiselect(key="f_categoria").set_value(["Universidad pública"]).run()
    assert not at.exception
    df = tabla(at)
    assert len(df) == 1
    assert df["institucion"].tolist() == ["UNMSM"]


def test_p3_busqueda(db):
    at = app()
    at.text_input(key="f_busqueda").input("PUCP").run()
    assert not at.exception
    assert len(tabla(at)) == 1


def test_p4_sin_resultados(db):
    at = app()
    at.text_input(key="f_busqueda").input("zzzxyz-inexistente").run()
    assert not at.exception
    assert metricas(at)["Noticias"] == "0"
    assert len(at.info) >= 1


def test_p5_csv(db):
    oes_db, _ = db
    df = oes_db.filtrar(oes_db.leer_noticias(), categorias=["Universidad privada"])
    datos = oes_db.a_csv(df)
    texto = datos.decode("utf-8-sig")
    cab = texto.splitlines()[0]
    assert cab.startswith("titulo,institucion,categoria") or "titulo" in cab
    for c in ("titulo", "institucion", "categoria", "url"):
        assert c in cab.split(",")
    leido = pd.read_csv(BytesIO(texto.encode("utf-8")))
    assert leido["institucion"].tolist() == ["PUCP"]
    # Botón de descarga: AppTest de esta versión puede no exponerlo.
    at = app()
    if hasattr(at, "download_button"):
        assert len(at.download_button) >= 1
    # (si AppTest no expone download_button se omite esta parte)


def test_p6_insertar_verificada(db):
    oes_db, _ = db
    d = nueva()
    ok, msg = oes_db.insertar_noticia(d)
    assert ok, msg
    df = oes_db.leer_noticias()
    assert len(df) == 4
    assert d["url"] in df["url"].tolist()
    at = app()
    m = metricas(at)
    assert m["Noticias"] == "4"
    assert m["Verificadas"] == "1"


def test_rechaza_url_marcador(db):
    oes_db, _ = db
    assert oes_db.validar_noticia(nueva(url="https://URL-DIRECTA-DE-LA-NOTA"))
    ok, _ = oes_db.insertar_noticia(nueva(url="https://URL-DIRECTA-DE-LA-NOTA"))
    assert not ok


def test_rechaza_fechas(db):
    oes_db, _ = db
    assert oes_db.validar_noticia(nueva(fecha="12/11/2026"))
    futura = (date.today() + timedelta(days=30)).isoformat()
    assert oes_db.validar_noticia(nueva(fecha=futura))


def test_rechaza_categoria(db):
    oes_db, _ = db
    assert oes_db.validar_noticia(nueva(categoria="Otra categoría"))


def test_verificada_sin_verificador(db):
    oes_db, _ = db
    assert oes_db.validar_noticia(nueva(verificado_por=""))
    ok, _ = oes_db.insertar_noticia(nueva(verificado_por=""))
    assert not ok


def test_duplicada(db):
    oes_db, _ = db
    assert oes_db.insertar_noticia(nueva())[0]
    ok, msg = oes_db.insertar_noticia(nueva())
    assert not ok
    assert "Duplicada" in msg


def test_filtro_fechas(db):
    oes_db, _ = db
    df = oes_db.filtrar(oes_db.leer_noticias(), desde=date(2026, 11, 6), hasta=date(2026, 11, 6))
    assert len(df) == 2
