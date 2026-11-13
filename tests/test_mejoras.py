"""Pruebas de mejoras: seguridad CSV y escritura del formulario Registrar."""
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
APP = str(RAIZ / "app.py")
sys.path.insert(0, str(RAIZ))


@pytest.fixture
def ruta_db(tmp_path, monkeypatch):
    ruta = tmp_path / "oes_mej.db"
    monkeypatch.setenv("OES_DB", str(ruta))
    r = subprocess.run([sys.executable, str(RAIZ / "preparar_datos.py")], env=os.environ.copy(),
                       cwd=str(RAIZ), capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    return ruta


def filas(ruta):
    con = sqlite3.connect(str(ruta))
    try:
        return con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
    finally:
        con.close()


def test_csv_neutraliza_formulas():
    import oes_db
    df = pd.DataFrame({"a": ["=1+1", "+x", "-y", "@z", "\tq", "\rr", "normal"], "n": range(7)})
    original = df.copy()
    texto = oes_db.a_csv(df).decode("utf-8-sig")
    lineas = texto.splitlines()
    assert "'=1+1,0" in lineas[1] and "'+x" in lineas[2] and "'-y" in lineas[3]
    assert "'@z" in lineas[4] and "'\tq" in texto and "normal,6" in texto
    pd.testing.assert_frame_equal(df, original)


def test_csv_normal_no_cambia():
    import oes_db
    df = pd.DataFrame({"a": ["hola", "mundo"], "n": [1, -2]})
    assert oes_db.a_csv(df) == df.to_csv(index=False).encode("utf-8-sig")


def _enviar(clave):
    at = AppTest.from_file(APP, default_timeout=30)
    at.secrets["clave_registro"] = "prueba123"
    at.run()
    assert not at.exception
    at.text_input(key="f_clave").set_value(clave).run()
    def campo(etq):
        return next(w for w in at.text_input if w.label == etq)
    campo("Título").set_value("Nota verificada de prueba mejoras")
    campo("Institución").set_value("MINEDU")
    campo("Fuente").set_value("gob.pe")
    campo("URL directa de la nota").set_value(
        "https://www.gob.pe/institucion/minedu/noticias/99999-nota-mejoras")
    campo("Verificado por (obligatorio si es Verificada)").set_value("Agente U2 (IA)")
    next(w for w in at.text_area if w.label.startswith("Resumen")).set_value("Resumen propio.")
    next(w for w in at.selectbox if w.label == "Categoría" and w.key != "f_categoria").set_value("Ente rector")
    next(w for w in at.selectbox if w.label == "Estado de verificación").set_value("Verificada")
    return at


def _boton(at):
    return next(b for b in at.button if b.label == "Registrar noticia")


def test_registrar_con_clave_correcta_inserta(ruta_db):
    assert filas(ruta_db) == 3
    at = _enviar("prueba123")
    _boton(at).click().run()
    assert not at.exception
    assert filas(ruta_db) == 4


def test_registrar_con_clave_incorrecta_no_inserta(ruta_db):
    """Con clave incorrecta el formulario no se muestra y la base no cambia."""
    at = AppTest.from_file(APP, default_timeout=30)
    at.secrets["clave_registro"] = "prueba123"
    at.run()
    at.text_input(key="f_clave").set_value("incorrecta").run()
    assert not at.exception
    assert not [w for w in at.text_input if w.label == "Título"]
    assert not [b for b in at.button if b.label == "Registrar noticia"]
    assert filas(ruta_db) == 3
