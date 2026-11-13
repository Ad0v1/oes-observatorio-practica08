# -*- coding: utf-8 -*-
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

RAIZ = Path(__file__).resolve().parent.parent
CAP = RAIZ / "informe" / "capturas-web"
SALIDA = RAIZ / "entregables" / "Manual_de_Usuario_OES.docx"
URL = "https://ad0v1-oes-observatorio-practica08-app-qcrrse.streamlit.app/"
TITULO = "Manual de usuario — Observatorio de Educación Superior (OES)"

d = Document()
sec = d.sections[0]
for a in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, a, Cm(2.5))

for nombre in ("Normal", "Heading 1", "Heading 2", "Caption", "List Number", "List Bullet"):
    st = d.styles[nombre]
    st.font.name = "Calibri"
    rpr = st.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for att in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(att), "Calibri")
    for att in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(att)) is not None:
            del rf.attrib[qn(att)]
d.styles["Normal"].font.size = Pt(11)
d.styles["Normal"].paragraph_format.space_after = Pt(6)
for n, s in (("Heading 1", 16), ("Heading 2", 13)):
    d.styles[n].font.size = Pt(s)

fig = [0]


def p(texto, bold=False, italic=False, align=None, size=None):
    par = d.add_paragraph()
    r = par.add_run(texto)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    if align is not None:
        par.alignment = align
    return par


def codigo(texto, size=10):
    q = p(texto)
    q.runs[0].font.name = "Consolas"
    q.runs[0].font.size = Pt(size)
    q.paragraph_format.space_after = Pt(2)
    return q


def h1(t): d.add_heading(t, 1)
def h2(t): d.add_heading(t, 2)


def pasos(lista):
    # Numeración manual: cada lista de pasos empieza en 1.
    for i, x in enumerate(lista, 1):
        p = d.add_paragraph(f"{i}. {x}")
        p.paragraph_format.left_indent = Cm(0.9)
        p.paragraph_format.first_line_indent = Cm(-0.6)
        p.paragraph_format.space_after = Pt(3)


def vinetas(lista):
    for x in lista:
        d.add_paragraph(x, style="List Bullet")


def figura(archivo, pie, ancho=15):
    fig[0] += 1
    par = d.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.keep_with_next = True
    par.add_run().add_picture(str(CAP / archivo), width=Cm(ancho))
    c = d.add_paragraph(f"Figura {fig[0]}. {pie}", style="Caption")
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER


def bordes(t):
    b = OxmlElement("w:tblBorders")
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        x = OxmlElement(f"w:{e}")
        x.set(qn("w:val"), "single")
        x.set(qn("w:sz"), "4")
        x.set(qn("w:color"), "808080")
        b.append(x)
    t._tbl.tblPr.append(b)


def tabla(cab, filas, anchos):
    t = d.add_table(rows=1, cols=len(cab))
    bordes(t)
    for i, c in enumerate(cab):
        cel = t.rows[0].cells[i]
        cel.text = ""
        cel.paragraphs[0].add_run(c).bold = True
        sh = OxmlElement("w:shd")
        sh.set(qn("w:val"), "clear")
        sh.set(qn("w:fill"), "D9E2F3")
        cel._tc.get_or_add_tcPr().append(sh)
    for f in filas:
        cs = t.add_row().cells
        for i, v in enumerate(f):
            cs[i].text = v
    for row in t.rows:
        for i, w in enumerate(anchos):
            row.cells[i].width = Cm(w)
    d.add_paragraph()


def campo(par, instr):
    r = par.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    r._r.append(f1); r._r.append(it); r._r.append(f2)


C = WD_ALIGN_PARAGRAPH.CENTER
# ---------- Portada ----------
for _ in range(5):
    d.add_paragraph()
p(TITULO, bold=True, align=C, size=26)
p("Prototipo académico", align=C, size=16, italic=True)
d.add_paragraph()
p("Curso: Inteligencia Artificial aplicada al Marketing Digital", align=C, size=13)
p("Universidad Nacional de Cañete (UNDC)", align=C, size=13)
d.add_paragraph()
p("Integrantes: [Completar nombres de los integrantes]", align=C)
p("Fecha: 13/11/2026", align=C)
p("Versión 1.0", align=C)
d.add_page_break()

# ---------- 1 ----------
h1("1. ¿Qué es y para qué sirve?")
p("El Observatorio de Educación Superior (OES) es una página web de consulta que reúne noticias de universidades "
  "y entidades de la educación superior peruana. Permite filtrarlas, buscarlas, ver gráficos y descargarlas en una "
  "hoja de cálculo. Cada noticia indica su fuente y si fue verificada contra la nota original.")
p("Sirve para ver de un vistazo qué comunica cada institución (admisión, becas, investigación, imagen) y apoyar "
  "decisiones de marketing. Es un prototipo académico: no reproduce el OES comercial.")
p("Enlace de la aplicación pública (solo lectura):")
p(URL, bold=True)

# ---------- 2 ----------
h1("2. Cómo ingresar")
pasos([
    "Abra el enlace anterior en cualquier navegador (Chrome, Edge, Firefox) desde su computadora o celular. No necesita usuario ni contraseña.",
    "Si ve un mensaje de que la aplicación está “dormida” (por falta de visitas), pulse el botón para despertarla y espere cerca de 1 minuto.",
    "Cuando cargue, verá el título “Observatorio de Educación Superior — Prototipo académico”, los filtros a la izquierda y las pestañas al centro.",
])

# ---------- 3 ----------
h1("3. Recorrido por la pantalla")
h2("3.1 Barra lateral de filtros y métricas")
p("A la izquierda está la barra “Filtros”: Categoría (Ente rector, Universidad privada, Universidad pública), "
  "Estado de verificación (Ejemplo didáctico, Verificada), Rango de fechas y un cuadro “Buscar título o institución”. "
  "Cada opción activa aparece como una etiqueta roja que se quita con la “x”. Todo lo que cambie aquí actualiza "
  "las métricas, los gráficos y la tabla.")
p("Debajo del título hay cuatro métricas: Noticias, Instituciones, Categorías y Verificadas. En la captura se leen "
  "7 noticias, 4 instituciones, 3 categorías y 4 verificadas. Cambian cuando usted filtra.")
figura("web-01-inicio-panorama.jpg", "Pantalla de inicio: filtros a la izquierda, métricas arriba y pestañas Panorama, Noticias, Registrar y Metodología.")
h2("3.2 Pestaña Panorama: gráficos")
p("Panorama muestra dos gráficos de barras: “Noticias por categoría” y “Noticias por tema” (Imagen institucional y eventos, "
  "Investigación e innovación, Admisión y captación, Becas y financiamiento). Cuanto más alta la barra, más noticias. "
  "Los gráficos son fijos: la rueda del ratón no los acerca ni los aleja.")
figura("web-02-graficos-categoria-tema.jpg", "Gráficos de noticias por categoría (parte superior) y por tema (parte inferior).")
h2("3.3 Matriz institución × tema (enfoque de marketing)")
p("Más abajo, la matriz cruza cada institución con los temas de sus noticias. Se calcula solo con noticias en estado "
  "Verificada. Cada columna apilada muestra cuántas noticias tiene la institución en cada tema (color) y la tabla "
  "inferior da los números exactos.")
p("Cómo leerla para marketing: en la captura, PUCP concentra sus noticias en Imagen institucional y eventos (2) e "
  "Investigación e innovación (1), mientras que UNDC aparece con Admisión y captación (1). Es decir, muestra en qué "
  "temas comunica más cada institución y en cuáles tiene poca presencia. Describe frecuencia, no mide calidad ni impacto.")
figura("web-03-matriz-marketing.jpg", "Matriz institución × tema, calculada solo con noticias verificadas, y su tabla de apoyo.")
h2("3.4 Pestaña Noticias")
p("Muestra una tabla con fecha, institución, categoría, tema, título, fuente, estado de verificación y una columna "
  "con el enlace “Abrir nota”, que lleva a la nota original en el sitio de la institución (puede desplazarse a la derecha "
  "para verla). Las notas marcadas como “Ejemplo: …” son registros didácticos.")
figura("web-04-noticias-tabla.jpg", "Tabla de noticias con las columnas fecha, institución, categoría, tema y título. Debajo aparece el botón Exportar CSV.")
h2("3.5 Buscar por texto")
p("Escriba una palabra en “Buscar título o institución” (por ejemplo, PUCP). La tabla y las métricas se reducen a las "
  "coincidencias: en la captura quedan 4 noticias de 1 institución.")
figura("web-06-busqueda-PUCP.jpg", "Búsqueda “PUCP”: las métricas pasan a 4 noticias, 1 institución y 3 verificadas.")
h2("3.6 Exportar CSV, paso a paso")
pasos([
    "Aplique los filtros que desee (opcional).",
    "Entre a la pestaña Noticias.",
    "Baje debajo de la tabla y pulse el botón “Exportar CSV”.",
    "Se descarga el archivo oes_resultados.csv con exactamente las filas que ve en pantalla.",
    "Ábralo con Excel (ver sección 4, tarea 6).",
])
h2("3.7 Pestaña Registrar (modo solo lectura)")
p("En la versión pública esta pestaña solo muestra el aviso “Modo solo lectura”: no se pueden agregar noticias desde la web. "
  "Esto evita que cualquier visitante modifique los datos. El registro lo hace el equipo administrador en su computadora (sección 5).")
figura("web-05-registrar-solo-lectura.jpg", "La pestaña Registrar en la web pública muestra “Modo solo lectura”.")
h2("3.8 Pestaña Metodología")
p("Explica de dónde salen las noticias (sitios y comunicados oficiales), cómo se verifican (contra la URL directa, "
  "indicando quién verificó), que los tres registros iniciales son “Ejemplo didáctico” y no deben citarse como evidencia, "
  "y los límites: un conteo de noticias no mide calidad ni impacto.")
figura("web-07-metodologia.jpg", "Pestaña Metodología: fuentes, verificación, registros DEMO, alcance y límites.")

# ---------- 4 ----------
h1("4. Tareas frecuentes")
h2("Tarea 1. Filtrar por tipo de institución")
pasos(["En “Categoría” de la barra lateral, pulse la “x” de las categorías que no quiere ver (por ejemplo, quite Ente rector y Universidad privada).",
       "Quedará solo “Universidad pública”. Las métricas, gráficos y tabla se actualizan."])
h2("Tarea 2. Ver solo noticias verificadas")
pasos(["En “Estado de verificación”, pulse la “x” de “Ejemplo didáctico”.", "Quedará solo “Verificada”."])
h2("Tarea 3. Filtrar por fechas")
pasos(["Pulse el campo “Rango de fechas”.",
       "Elija la fecha inicial y luego la final en el calendario, o escríbalas en formato AAAA/MM/DD.",
       "La información se limita a ese periodo."])
h2("Tarea 4. Buscar una institución")
pasos(["Escriba su nombre o sigla (por ejemplo, UNDC) en “Buscar título o institución”.", "Pulse Enter. Se filtra la tabla."])
h2("Tarea 5. Restablecer los filtros")
pasos(["Para quitar la búsqueda, borre el texto del cuadro.",
       "Para volver a incluir una categoría o estado, ábralo con la flecha y elíjalo de nuevo; las etiquetas se quitan con la “x”.",
       "Para volver todo al estado inicial, recargue la página (tecla F5)."])
h2("Tarea 6. Descargar resultados en CSV y abrirlos en Excel")
pasos(["Siga los pasos de la sección 3.6 para descargar oes_resultados.csv.",
       "En Excel, use Datos > Obtener datos > Desde texto/CSV, elija el archivo y en “Origen del archivo” seleccione UTF-8.",
       "Pulse Cargar. Así las tildes y la ñ se ven bien."])

# ---------- 5 ----------
h1("5. Para el equipo que administra")
p("Esta sección es técnica. Se asume Windows y Python 3.11.")
h2("5.1 Ejecutar en local")
for c in ["py -3.11 -m venv .venv",
          ".venv\\Scripts\\activate     (si PowerShell lo bloquea: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned)",
          "python -m pip install -r requirements.txt",
          "python preparar_datos.py     (crea oes.db con los 3 registros DEMO; no duplica si se repite)",
          "streamlit run app.py         (abre http://localhost:8501)"]:
    codigo(c)
d.add_paragraph()
h2("5.2 Registrar noticias")
p("Opción A: formulario. En local, la pestaña Registrar muestra un formulario (título, institución, categoría, fuente, "
  "fecha, URL directa, resumen, tema, estado y “Verificado por”). Si se definió la clave clave_registro en los secrets, "
  "se pide al entrar.")
figura("web-09-registrar-local-formulario.jpg", "Formulario de registro en ejecución local (captura de baja resolución).", ancho=7)
p("Opción B: línea de comandos, una noticia:")
codigo('python agregar_noticia.py --titulo "..." --institucion "SUNEDU" --categoria "Ente regulador" --fuente "..." '
       '--fecha 2026-11-10 --url "https://..." --resumen "..." --tema "..." --verificado-por "Nombre"', 9)
p("Por lotes desde un CSV:")
codigo("python agregar_noticia.py --csv datos\\noticias_univ.csv")
d.add_paragraph()
h2("5.3 Reglas de validación")
vinetas(["La fecha debe tener formato AAAA-MM-DD y no puede ser futura.",
         "Una noticia verificada necesita URL directa de la nota (no la portada del sitio) y el nombre de quien la verificó.",
         "Se rechazan los marcadores de ejemplo en registros reales.",
         "Se rechazan URLs duplicadas (cargar dos veces el mismo lote no duplica filas).",
         "Antes de marcar “Verificada”, abra la nota original y compare titular y fecha."])
h2("5.4 Actualizar la web pública")
p("La aplicación en la nube no guarda altas (su disco no es permanente). Procedimiento: cargar las noticias en local, "
  "subir el archivo oes.db actualizado al repositorio de GitHub (https://github.com/Ad0v1/oes-observatorio-practica08) y "
  "la web pública se actualiza sola en unos minutos. Para comprobar el funcionamiento: python -m pytest tests -q (13 pruebas).")

# ---------- 6 ----------
h1("6. Preguntas frecuentes y solución de problemas")
tabla(["Problema o pregunta", "Causa y solución"], [
    ("La página no carga o pide “despertar” la app.", "Streamlit duerme las apps sin visitas. Pulse el botón de reactivar y espere cerca de 1 minuto."),
    ("No aparecen datos / la tabla está vacía.", "Revise los filtros: puede haber quitado todas las categorías o estados. Recargue la página (F5) para volver a los valores iniciales."),
    ("Sale “No hay resultados con esos filtros” (0 resultados).", "Ninguna noticia cumple la combinación. Amplíe el rango de fechas, borre el texto de búsqueda o vuelva a agregar categorías. No es un error."),
    ("¿Por qué veo noticias que dicen “Ejemplo didáctico”?", "Son 3 registros ilustrativos de la guía (PRONABEC, UNMSM, PUCP). No son información verificada ni deben citarse. Quítelos en Estado de verificación."),
    ("¿Por qué no puedo registrar noticias en la web?", "La versión pública es de solo lectura, para proteger los datos. El registro se hace en local y luego se sube oes.db."),
    ("El CSV muestra tildes o ñ raras (Ã³, Ã±).", "Excel lo abrió con otra codificación. Impórtelo con Datos > Desde texto/CSV y elija UTF-8."),
    ("La matriz institución × tema muestra pocas instituciones.", "Solo usa noticias en estado Verificada, y hoy hay 4. Mientras más noticias verificadas se carguen, más completa será."),
    ("El enlace “Abrir nota” no abre o la página cambió.", "La institución pudo mover o retirar la nota. Búsquela en su sitio oficial o avise al equipo para corregir el registro."),
], [6, 10])

# ---------- 7 ----------
h1("7. Glosario")
tabla(["Término", "Significado"], [
    ("Categoría", "Tipo de institución que publica la noticia: Ente rector, Universidad privada o Universidad pública."),
    ("Tema", "Asunto principal de la noticia: Admisión y captación, Becas y financiamiento, Investigación e innovación, Imagen institucional y eventos."),
    ("Estado de verificación", "Indica si la noticia fue contrastada con su nota original (Verificada), está por revisar (Pendiente) o es un registro de práctica (Ejemplo didáctico)."),
    ("Matriz institución × tema", "Tabla/gráfico que cruza cada institución con los temas de sus noticias verificadas, para ver en qué comunica más cada una."),
    ("CSV", "Archivo de texto con datos separados por comas que se abre en Excel."),
    ("Modo solo lectura", "La web permite consultar y descargar, pero no agregar ni cambiar noticias."),
], [5, 11])

# ---------- encabezado / pie ----------
hp = sec.header.paragraphs[0]
hp.text = TITULO
hp.runs[0].font.size = Pt(9)
fp = sec.footer.paragraphs[0]
fp.alignment = C
fp.add_run("Versión 1.0 · Página ")
campo(fp, "PAGE")
for r in fp.runs:
    r.font.size = Pt(9)

d.save(SALIDA)
print("OK", SALIDA)
