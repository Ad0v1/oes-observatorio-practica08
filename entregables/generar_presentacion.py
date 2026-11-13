from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image
import os

R = r"C:\Construccion por codigo\oes_laboratorio"
CAP = R + r"\informe\capturas-web"
OUT = R + r"\entregables\Presentacion_OES.pptx"
AZUL = RGBColor(0x1F, 0x4E, 0x79)
ROJO = RGBColor(0xC0, 0x39, 0x2B)
GRIS = RGBColor(0x33, 0x33, 0x33)
BLANCO = RGBColor(255, 255, 255)
APP = "https://ad0v1-oes-observatorio-practica08-app-qcrrse.streamlit.app/"
REPO = "https://github.com/Ad0v1/oes-observatorio-practica08"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]
total = 12


def text(slide, x, y, w, h, s, size=20, bold=False, color=GRIS, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = s
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = "Calibri"
    return tb


def bullets(slide, x, y, w, h, items, size=20, gap=10):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        r0 = p.add_run()
        r0.text = "\u25A0  "
        r0.font.size = Pt(size - 6)
        r0.font.color.rgb = ROJO
        r = p.add_run()
        r.text = it
        r.font.size = Pt(size)
        r.font.color.rgb = GRIS
        r.font.name = "Calibri"
    return tb


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
    s.shadow.inherit = False
    return s


def label(shape, s, size=18, color=BLANCO, bold=True):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = s
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = "Calibri"


def pic(slide, path, x, y, mw, mh, center=True):
    iw, ih = Image.open(path).size
    k = min(mw / iw, mh / ih)
    w, h = iw * k, ih * k
    px = x + (mw - w) / 2 if center else x
    p = slide.shapes.add_picture(path, Inches(px), Inches(y), Inches(w), Inches(h))
    p.line.color.rgb = RGBColor(0xBB, 0xBB, 0xBB)
    p.line.width = Pt(1)
    return px, y, w, h


def new(n, title, notes):
    s = prs.slides.add_slide(blank)
    rect(s, 0, 0, 0.25, 7.5, AZUL, shape=MSO_SHAPE.RECTANGLE)
    text(s, 0.6, 0.3, 12.1, 0.9, title, 34, True, AZUL, anchor=MSO_ANCHOR.MIDDLE)
    ln = rect(s, 0.65, 1.2, 1.6, 0.06, ROJO, shape=MSO_SHAPE.RECTANGLE)
    text(s, 11.9, 6.95, 1.2, 0.4, f"{n} / {total}", 18, False, AZUL, PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text = notes
    return s


# 1 Portada
s = prs.slides.add_slide(blank)
rect(s, 0, 0, 13.333, 7.5, AZUL, shape=MSO_SHAPE.RECTANGLE)
rect(s, 0.9, 3.55, 2.2, 0.08, ROJO, shape=MSO_SHAPE.RECTANGLE)
text(s, 0.9, 1.2, 11.5, 2.3, "Observatorio de Educación Superior (OES)", 44, True, BLANCO, anchor=MSO_ANCHOR.BOTTOM)
text(s, 0.9, 3.8, 11.5, 0.6, "Prototipo académico con Python, SQLite y Streamlit", 28, False, BLANCO)
text(s, 0.9, 4.7, 11.5, 0.5, "Inteligencia Artificial aplicada al Marketing Digital", 22, False, BLANCO)
text(s, 0.9, 5.15, 11.5, 0.5, "Universidad Nacional de Cañete (UNDC) · Práctica 08", 22, False, BLANCO)
text(s, 0.9, 5.9, 11.5, 0.5, "Integrantes: [Completar nombres de los integrantes]", 20, False, BLANCO)
text(s, 0.9, 6.4, 11.5, 0.5, "13/11/2026", 20, False, BLANCO)
s.notes_slide.notes_text_frame.text = "Presentamos el Observatorio de Educación Superior, un prototipo académico de la Práctica 08. Mencionar integrantes, curso y fecha."

# 2 Problema
s = new(2, "El problema y el objetivo",
        "Un observatorio reúne y ordena información de un sector para poder analizarla. La práctica pedía un prototipo mínimo: base de datos, tablero web, pruebas y publicación. Enfatizar que es un prototipo, no un producto final.")
bullets(s, 0.7, 1.7, 7.2, 4.6, [
    "Observatorio: reúne noticias del sector y las ordena para analizarlas",
    "Pedido de la práctica: guardar noticias en una base de datos",
    "Mostrarlas en un tablero web con filtros y gráficos",
    "Probar que funciona (P1 a P6) y publicarlo",
    "Mirada de marketing: qué comunica cada institución",
], 24, 14)
b = rect(s, 8.5, 1.9, 4.2, 3.6, AZUL)
label(b, "Noticias \u2192 base de datos \u2192 tablero web", 26)
text(s, 8.5, 5.7, 4.2, 0.8, "Del dato suelto a la lectura clara", 20, True, ROJO, PP_ALIGN.CENTER)

# 3 Arquitectura
s = new(3, "Cómo funciona",
        "El diagrama muestra el flujo: los scripts preparan y validan los datos en SQLite; la capa de datos los entrega a la app Streamlit, que muestra filtros, gráficos y tabla. Una sola idea: los datos entran validados y se leen en la web.")
pic(s, R + r"\informe\arquitectura.png", 1.9, 1.4, 9.5, 4.85)
text(s, 0.7, 6.4, 11, 0.5, "Scripts validan y guardan en SQLite; la app Streamlit solo lee y muestra.", 20, False, GRIS)

# 4 La web
s = new(4, "La web",
        "Esta es la página de inicio. A la izquierda los filtros: categoría, estado de verificación, fechas y búsqueda. Arriba cuatro métricas: 7 noticias, 4 instituciones, 3 categorías, 4 verificadas. Debajo las pestañas Panorama, Noticias, Registrar y Metodología.")
pic(s, CAP + r"\web-01-inicio-panorama.jpg", 0.6, 1.6, 8.4, 4.6, center=False)
for i, (t, d) in enumerate([("1  Filtros", "categoría, estado, fechas, búsqueda"),
                            ("2  Métricas", "7 noticias · 4 instituciones · 3 categorías · 4 verificadas"),
                            ("3  Pestañas", "Panorama, Noticias, Registrar, Metodología")]):
    y = 1.7 + i * 1.5
    rect(s, 9.3, y, 3.5, 1.3, RGBColor(0xEA, 0xF0, 0xF6), AZUL)
    text(s, 9.4, y + 0.05, 3.3, 0.45, t, 22, True, ROJO)
    text(s, 9.4, y + 0.5, 3.3, 0.8, d, 18)

# 5 Gráficos
s = new(5, "Gráficos y enfoque de marketing",
        "La matriz cruza institución por tema, usando solo noticias verificadas. Se lee así: la PUCP comunica sobre todo imagen institucional y eventos; la UNDC comunica admisión y captación. Aclarar que la matriz describe qué comunica cada institución y no mide calidad.")
pic(s, CAP + r"\web-03-matriz-marketing.jpg", 0.6, 1.6, 7.8, 4.6, center=False)
bullets(s, 8.7, 1.7, 4.2, 4.6, [
    "Matriz institución \u00D7 tema",
    "PUCP: imagen y eventos",
    "UNDC: admisión y captación",
    "Solo noticias verificadas",
    "Describe lo que comunican; no mide calidad",
], 20, 12)

# 6 Noticias y exportación
s = new(6, "Noticias, búsqueda y exportación",
        "A la izquierda la tabla de noticias con su enlace directo y el botón para exportar a CSV. A la derecha, la búsqueda por texto: al escribir PUCP se filtran solo sus noticias.")
pic(s, CAP + r"\web-04-noticias-tabla.jpg", 0.5, 1.6, 6.1, 3.5, center=False)
pic(s, CAP + r"\web-06-busqueda-PUCP.jpg", 6.8, 1.6, 6.1, 3.5, center=False)
text(s, 0.5, 5.3, 6.1, 0.9, "Tabla con enlace y botón Exportar CSV", 20, True, AZUL)
text(s, 6.8, 5.3, 6.1, 0.9, "Búsqueda por título o institución (ej.: PUCP)", 20, True, AZUL)
text(s, 0.5, 6.2, 11, 0.5, "Lo filtrado en pantalla es lo que se exporta.", 20, False, ROJO)

# 7 Datos confiables
s = new(7, "Datos confiables",
        "Cada noticia real se verificó con URL directa, fecha y estado. Los scripts validan la fecha, rechazan marcadores y duplicados. En la web pública el registro está en solo lectura, como se ve en la captura.")
bullets(s, 0.7, 1.7, 6.2, 4.8, [
    "Verificación: URL directa, fecha y estado",
    "Fecha AAAA-MM-DD y no futura",
    "Rechaza marcadores y duplicados",
    "Ejemplos de la guía marcados «Ejemplo didáctico»",
    "Web pública: registro en solo lectura",
], 22, 14)
pic(s, CAP + r"\web-05-registrar-solo-lectura.jpg", 7.1, 1.9, 5.8, 3.2, center=False)
text(s, 7.1, 5.2, 5.8, 0.6, "Registrar en modo solo lectura", 20, True, AZUL)

# 8 Pruebas
s = new(8, "Pruebas P1 a P6",
        "Las seis pruebas de la guía se pasaron. Además hay 13 pruebas automáticas con pytest, todas aprobadas.")
rows = [("P1", "Dos cargas seguidas → 3 filas, sin duplicar"),
        ("P2", "Filtro Universidad pública → UNMSM"),
        ("P3", "Buscar PUCP → 1 fila"),
        ("P4", "Término inexistente → 0 filas y aviso, sin error"),
        ("P5", "Exportar CSV con encabezados y filas filtradas"),
        ("P6", "4 noticias reales: de 3 a 7, URL conservada")]
tbl = s.shapes.add_table(len(rows) + 1, 3, Inches(0.7), Inches(1.6), Inches(11.9), Inches(4.2)).table
tbl.columns[0].width = Inches(1.1)
tbl.columns[1].width = Inches(9.5)
tbl.columns[2].width = Inches(1.3)
for j, h in enumerate(["Prueba", "Resultado esperado", "Estado"]):
    c = tbl.cell(0, j)
    c.text = h
    c.fill.solid(); c.fill.fore_color.rgb = AZUL
    r = c.text_frame.paragraphs[0].runs[0]
    r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = BLANCO
for i, (a, b_) in enumerate(rows, 1):
    for j, v in enumerate([a, b_, "\u2713"]):
        c = tbl.cell(i, j)
        c.text = v
        c.fill.solid(); c.fill.fore_color.rgb = RGBColor(0xF4, 0xF7, 0xFA) if i % 2 else BLANCO
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = c.text_frame.paragraphs[0].runs[0]
        r.font.size = Pt(18); r.font.bold = (j != 1)
        r.font.color.rgb = ROJO if j == 2 else GRIS
        if j == 2:
            c.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
b = rect(s, 0.7, 6.0, 5.2, 0.8, ROJO)
label(b, "13/13 pruebas automáticas", 22)

# 9 Cómo lo construimos
s = new(9, "Cómo lo construimos",
        "Trabajó un equipo de agentes de IA coordinado por un orquestador. Hubo cuatro rondas, cada agente con un máximo de 8 minutos y sin subagentes. Se comunicaban por archivos: un contrato y entregas por agente.")
o = rect(s, 0.8, 3.0, 2.6, 1.3, AZUL); label(o, "Orquestador", 22)
names = ["Datos", "App", "Pruebas", "Informe"]
for i, n in enumerate(names):
    y = 1.6 + i * 1.15
    a = rect(s, 5.2, y, 2.4, 0.85, RGBColor(0xEA, 0xF0, 0xF6), AZUL)
    label(a, "Agente " + n, 20, AZUL)
    c = s.shapes.add_connector(1, Inches(3.4), Inches(3.65), Inches(5.2), Inches(y + 0.42))
    c.line.color.rgb = AZUL; c.line.width = Pt(2)
k = rect(s, 8.2, 1.6, 4.6, 0.85, ROJO); label(k, "contrato.md + entregas", 20)
bullets(s, 8.2, 2.7, 4.6, 3.8, [
    "4 rondas de trabajo",
    "Máx. 8 min por agente",
    "Sin subagentes",
    "Coordinación por archivos",
], 20, 12)

# 10 Publicación
s = new(10, "Publicación",
        "El código está en un repositorio público de GitHub y la app corre en Streamlit Community Cloud, de forma pública y en solo lectura. La app se duerme sin visitas, así que puede tardar al abrir.")
pic(s, CAP + r"\web-08-repositorio-github.jpg", 0.6, 1.6, 7.6, 4.0, center=False)
bullets(s, 8.5, 1.7, 4.4, 2.4, [
    "Repo público en GitHub",
    "App en Streamlit Cloud",
    "Pública y solo lectura",
], 20, 10)
text(s, 0.6, 5.9, 12.2, 0.9, "App: " + APP, 18, True, AZUL)

# 11 Límites
s = new(11, "Límites y aprendizajes",
        "Ser honestos: gob.pe bloqueó el acceso automatizado y no se eludió, por eso no hay noticias reales de entes rectores. La verificación la hizo IA y falta confirmación humana del grupo. La nube no guarda altas. Y un conteo de noticias no mide calidad.")
bullets(s, 0.7, 1.7, 12, 4.8, [
    "gob.pe bloqueó el acceso automatizado: no hay noticias reales de entes",
    "Verificación hecha por IA: falta confirmación humana del grupo",
    "La app en la nube no guarda altas: se cargan en local",
    "Un conteo de noticias no mide calidad",
    "Aprendizaje: contrato claro y pruebas temprano",
], 24, 16)

# 12 Cierre
s = prs.slides.add_slide(blank)
rect(s, 0, 0, 13.333, 7.5, AZUL, shape=MSO_SHAPE.RECTANGLE)
text(s, 0.9, 1.0, 11.5, 1.2, "Gracias / Preguntas", 44, True, BLANCO)
rect(s, 0.9, 2.3, 2.2, 0.08, ROJO, shape=MSO_SHAPE.RECTANGLE)
text(s, 0.9, 2.8, 11.8, 0.5, "App pública", 22, True, BLANCO)
text(s, 0.9, 3.3, 11.8, 0.5, APP, 18, False, BLANCO)
text(s, 0.9, 4.2, 11.8, 0.5, "Repositorio", 22, True, BLANCO)
text(s, 0.9, 4.7, 11.8, 0.5, REPO, 18, False, BLANCO)
text(s, 11.9, 6.95, 1.2, 0.4, "12 / 12", 18, False, BLANCO, PP_ALIGN.RIGHT)
s.notes_slide.notes_text_frame.text = "Agradecer y abrir preguntas. Compartir los enlaces de la app y del repositorio."

prs.save(OUT)

# verificación de límites
bad = 0
for i, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.left < 0 or sh.top < 0 or sh.left + sh.width > prs.slide_width or sh.top + sh.height > prs.slide_height:
            print("FUERA", i, sh.shape_type, sh.name); bad += 1
print("diapositivas", len(prs.slides), "fuera:", bad)
