# -*- coding: utf-8 -*-
"""Genera Informe_Laboratorio_Practica08.docx (version final, ordenada segun la guia)."""
import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = Path(__file__).parent
ROOT = BASE.parent
INF = ROOT / "informe"
CAP = INF / "capturas-oes"
WEB = INF / "capturas-web"
INTEGRANTES = "[Completar nombres de los integrantes]"
TITULO = "Construcción de un Observatorio de Educación Superior (OES): El marketing en la educación"
APP = "https://ad0v1-oes-observatorio-practica08-app-qcrrse.streamlit.app/"
REPO = "https://github.com/Ad0v1/oes-observatorio-practica08"

B = []
def h1(t): B.append(("h1", t))
def h2(t): B.append(("h2", t))
def p(t): B.append(("p", t))
def li(t): B.append(("li", t))
def code(t): B.append(("code", t))
def tabla(rows, widths=None): B.append(("t", rows, widths))
def fig(path, cap, w=15): B.append(("f", path, w, cap))
def pb(): B.append(("pb",))

def leer(path, n=None):
    s = Path(path).read_text(encoding="utf-8-sig")
    lines = [l.rstrip() for l in s.splitlines() if l.strip()]
    return "\n".join(lines[:n] if n else lines)

# ============ TABLA DE CUMPLIMIENTO ============
h1("Tabla de cumplimiento de la guía")
p("Cada fila remite a la sección del informe y a la evidencia que la sustenta. El estado ✓ indica que el elemento fue entregado y verificado por el grupo de trabajo (agentes de IA coordinados) y debe ser confirmado por los integrantes.")
h2("A. Entregables del nivel básico (obligatorio)")
tabla([["Entregable", "Estado", "Dónde está la evidencia"],
 ["Diagrama de arquitectura", "✓", "Figura 1 (sección 2); archivo arquitectura.png"],
 ["Base de datos oes.db", "✓", "Archivo oes.db en el repositorio; tabla noticias (sección 5); 7 registros"],
 ["Scripts Python", "✓", "preparar_datos.py, agregar_noticia.py, oes_db.py, app.py, tests/test_oes.py (13 pruebas aprobadas); repositorio"],
 ["Captura del tablero", "✓", "Figura 2 (oes-01, 3/3/3), Figura 3 (web-01) y Figura 10 (oes-09, 7 noticias)"],
 ["Evidencias de las seis pruebas", "✓", "Sección 8: tabla P1–P6, capturas oes-03, oes-04, oes-05, oes-08, oes-09 y archivos oes-02, oes-06, oes-07"]], [4.5, 1.5, 10.0])
h2("B. Pasos de la guía")
tabla([["Paso", "Estado", "Dónde está la evidencia"],
 ["1. Instalar Python", "✓", "Sección 4 (Python 3.11 con el lanzador py; el comando python del equipo era 3.8)"],
 ["2. Crear proyecto y entorno virtual", "✓", "Sección 4; requirements.txt con versiones fijas"],
 ["3. Identificar entidades", "✓", "Sección 5: tabla de entidades y modelo implementado"],
 ["4. Crear y ejecutar preparar_datos.py", "✓", "Sección 5; evidencia oes-02 (sección 8, P1)"],
 ["5. Crear app.py", "✓", "Sección 6; app.py y oes_db.py en el repositorio"],
 ["6. Ejecutar y comprobar (3 noticias, 3 instituciones, 3 categorías)", "✓", "Sección 6; Figura 2 (oes-01)"],
 ["7. Incorporar fuentes reales verificadas", "✓", "Sección 7; 4 noticias reales; evidencias oes-07 y oes-08"]], [6.0, 1.5, 8.5])
h2("C. Criterios de la rúbrica (20 puntos) y evidencia que los sustenta")
p("La calificación corresponde a la docente; aquí solo se indica qué evidencia respalda cada criterio.")
tabla([["Criterio (puntaje)", "Evidencia que lo sustenta"],
 ["Arquitectura y explicación de flujo (4)", "Sección 2: Figura 1 y explicación del flujo fuente → captura → validación → almacenamiento → consulta → decisiones; sección 3 (requisitos)"],
 ["Base de datos y trazabilidad (4)", "Sección 5 (modelo, restricciones CHECK y UNIQUE, campos fecha_captura, verificado_por, estado_verificacion); sección 7 (URL directa y verificación)"],
 ["Aplicación funcional y filtros (5)", "Sección 6 (Figuras 2 a 5); aplicación pública (sección 12); 13 pruebas pytest aprobadas"],
 ["Pruebas y evidencias (4)", "Sección 8: P1–P6 con capturas y textos de evidencia"],
 ["Análisis crítico, ética y conclusiones (3)", "Secciones 10 y 11; anexo de correcciones a la guía"]], [5.5, 10.5])

pb()
# ============ 1 ============
h1("1. Propósito, delimitación y evidencias")
p("La comunicación de las instituciones de educación superior (admisión, becas, hitos de investigación, eventos, alianzas) es información pública dispersa en portales y comunicados. Un observatorio la reúne con fuente y fecha para poder compararla.")
p("**Objetivo general.** Diseñar, implementar y validar un prototipo local de observatorio que registre, clasifique, consulte y visualice novedades de educación superior peruana con trazabilidad de fuentes.")
p("**Resultados de aprendizaje y dónde se logran.** Identificar requisitos (sección 3); representar arquitectura y modelo de datos (secciones 2 y 5); construir una aplicación funcional (sección 6); verificar filtros, métricas y exportación (sección 8); argumentar límites éticos y metodológicos (secciones 10 y 11).")
p("**Delimitación.** El portal OES comercial declara tres plataformas (Tablero de Monitoreo Estratégico, OES Transparencia y OES Calidad), 115 fuentes y cuatro ciclos diarios de vigilancia (Observatorio de Educación Superior, 2026a). Son afirmaciones del proveedor, no mediciones verificadas en esta práctica. Este laboratorio reproduce solo funciones generales del monitoreo, sin copiar código, identidad gráfica ni contenidos protegidos.")
tabla([["Evidencia pública / alcance", "Lo que cubre el prototipo"],
 ["Monitoreo de entes y universidades", "Registro de fuentes e instituciones; noticias con fecha, categoría y enlace"],
 ["Ficha estructurada y filtro", "Dashboard local, filtros y exportación CSV"],
 ["Tableros e informes", "Panorama por categoría y tema; matriz institución × tema"],
 ["Transparencia y calidad; alertas y análisis con IA", "Extensiones propuestas, no implementadas (nivel avanzado)"]], [6.5, 9.5])
p("**Enlaces.** Aplicación pública (solo lectura): " + APP + " · Repositorio: " + REPO)

# ============ 2 ============
h1("2. Arquitectura de referencia")
p("Flujo general: **fuente → captura → validación → almacenamiento → consulta → decisiones**. La figura es una arquitectura académica propuesta; el sitio público del OES no revela su infraestructura ni tecnologías internas.")
fig(INF / "arquitectura.png", "Arquitectura del prototipo, distinguiendo lo implementado de lo propuesto.")
li("**Fuente:** sitios oficiales (MINEDU, SUNEDU, PRONABEC, CONCYTEC, SINEACE) y portales de universidades.")
li("**Captura:** registro manual mediante el formulario *Registrar*, el script `agregar_noticia.py` (campos por línea de comandos o carga desde CSV) y los registros DEMO de `preparar_datos.py`.")
li("**Validación:** `oes_db.validar_noticia` comprueba campos obligatorios, fecha AAAA-MM-DD no futura, URL directa sin marcadores, categoría, tema y estado permitidos, y exige verificador para el estado «Verificada». La base añade restricciones `CHECK` y `UNIQUE`.")
li("**Almacenamiento:** una tabla `noticias` en SQLite (oes.db), accedida solo desde `oes_db.py`.")
li("**Consulta:** filtros por categoría, estado de verificación, rango de fechas y texto; exportación a CSV.")
li("**Decisiones:** panorama por categoría y por tema, y matriz institución × tema para orientar la lectura del mensaje institucional, siempre con revisión humana.")
tabla([["Componente", "Estado"],
 ["Registro por formulario y por script, validación, tabla única SQLite, dashboard con filtros, panorama y exportación CSV", "Implementado"],
 ["Captura automática programada, múltiples plataformas, normalización en tres entidades, resumen asistido por IA con revisión, análisis prospectivo", "Propuesto (no implementado)"]], [12, 4])

# ============ 3 ============
h1("3. Requisitos y criterios de aceptación")
tabla([["ID", "Requisito (guía)", "Verificación (guía)", "Cómo lo cumple el prototipo", "Estado"],
 ["RF01", "Registrar noticia con fuente, institución, fecha, título, URL y categoría", "Registro aparece en tabla", "Formulario Registrar y agregar_noticia.py (CLI y CSV), con validación e informe de duplicados (evidencia oes-07; Figura 10).", "✓"],
 ["RF02", "Filtrar por categoría y texto", "Resultados cambian correctamente", "Filtros de categoría, estado, fechas y búsqueda por título o institución (Figuras 6 y 7).", "✓"],
 ["RF03", "Calcular indicadores", "Conteos coinciden con datos", "Métricas, barras por categoría y tema, y matriz institución × tema (Figuras 2, 5 y 10).", "✓"],
 ["RF04", "Exportar resultados", "Archivo CSV descargable", "Botón «Exportar CSV» (oes_resultados.csv, UTF-8 con BOM) sobre el resultado filtrado (evidencia oes-06).", "✓"],
 ["RNF01", "Trazabilidad y ética", "URL, fecha y fuente visibles", "Cada noticia conserva fuente, URL directa única, fecha, fecha de captura, verificador y estado.", "✓"],
 ["RNF02", "Funcionamiento local", "App inicia sin servicios de pago", "SQLite local, variable OES_DB, requirements.txt con versiones fijas; Python 3.11; sin servicios de pago.", "✓"]], [1.4, 3.6, 2.8, 6.8, 1.4])

# ============ 4 ============
h1("4. Preparación del entorno (Pasos 1 y 2)")
p("**Paso 1. Python.** La guía pide Python 3.11 o posterior. En el equipo de trabajo el comando `python` correspondía a la versión 3.8, que no es suficiente; se usó el lanzador de Windows con la versión indicada (`py -3.11 --version`).")
p("**Paso 2. Proyecto y entorno virtual.** Se creó la carpeta oes_laboratorio y el entorno con `py -3.11 -m venv .venv`. Se instalaron las dependencias con versiones fijas desde requirements.txt: Streamlit 1.67, pandas 3.1.1 y Altair 6.3 (la guía no mencionaba Altair, que Streamlit necesita para los gráficos de la aplicación).")
code("py -3.11 -m venv .venv\n.venv\\Scripts\\activate\npython -m pip install --upgrade pip\npip install -r requirements.txt")
p("**Nota sobre PowerShell.** Si la activación del entorno es bloqueada por la política de ejecución, se ejecuta una sola vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. Esta es una configuración del usuario del propio equipo de trabajo, no del sistema.")

# ============ 5 ============
h1("5. Diseño de datos (Paso 3) y carga inicial (Paso 4)")
h2("5.1 Entidades identificadas (Paso 3)")
tabla([["Entidad", "Campos principales", "Relación"],
 ["Institución", "id, nombre, tipo", "Una institución tiene muchas noticias"],
 ["Fuente", "id, nombre, url", "Una fuente puede originar muchas noticias"],
 ["Noticia", "id, titulo, fecha, categoria, url, resumen, institucion_id, fuente_id", "Cada noticia apunta a institución y fuente"]], [3, 8, 5])
p("Como indica la guía, para simplificar se implementa una tabla de noticias desnormalizada. Una consulta sin uniones, un esquema comprensible en una sesión y la carga directa desde CSV son las ventajas; el costo es la repetición de institución, categoría y fuente en cada fila, que permite inconsistencias (la misma institución escrita de dos formas). La normalización en las tres entidades queda propuesta, no implementada.")
h2("5.2 Modelo implementado")
tabla([["Columna", "Tipo", "Descripción / restricción"],
 ["id", "INTEGER", "Clave primaria autoincremental"],
 ["titulo", "TEXT NOT NULL", "Titular de la nota"],
 ["institucion", "TEXT NOT NULL", "Institución que publica"],
 ["categoria", "TEXT NOT NULL", "Tipo de institución: Ente rector, Ente regulador, Universidad pública, Universidad privada"],
 ["fuente", "TEXT NOT NULL", "Medio o portal de origen"],
 ["fecha", "TEXT NOT NULL", "AAAA-MM-DD, con CHECK (fecha = date(fecha))"],
 ["url", "TEXT NOT NULL UNIQUE", "URL directa de la nota; evita duplicados"],
 ["resumen", "TEXT NOT NULL", "Resumen de redacción propia"],
 ["tema", "TEXT NOT NULL (def. «Sin tema»)", "Tema de comunicación (marketing)"],
 ["estado_verificacion", "TEXT NOT NULL (def. «Ejemplo didáctico»)", "Ejemplo didáctico, Verificada o Pendiente"],
 ["fecha_captura", "TEXT NOT NULL (def. hoy)", "Fecha en que se registró"],
 ["verificado_por", "TEXT", "Persona o agente que verificó"]], [3.6, 4.6, 7.8])
h2("5.3 Carga inicial (Paso 4)")
p("`preparar_datos.py` crea la base oes.db y carga los tres registros demostrativos de la guía (PRONABEC, UNMSM, PUCP) con `INSERT OR IGNORE`, de modo que ejecutarlo varias veces no duplica filas. Estos registros llevan el estado «Ejemplo didáctico»: sus URL apuntan a portales institucionales, no a artículos concretos, y no se presentan como noticias verificadas. La ejecución doble se documenta en la prueba P1 (sección 8).")

# ============ 6 ============
h1("6. Construcción del dashboard (Pasos 5 y 6)")
p("**Paso 5.** `app.py` presenta el tablero; la lógica de datos y validación está en `oes_db.py`. Extiende la versión de la guía con filtros por categoría, estado de verificación y rango de fechas, búsqueda por título o institución, métricas, pestañas Panorama (barras por categoría y por tema, y matriz institución × tema), Noticias (tabla con enlace y botón Exportar CSV), Registrar (formulario) y Metodología. Los gráficos son estáticos para que la rueda del ratón no los amplíe al desplazarse por la página.")
p("**Paso 6.** Al ejecutar `streamlit run app.py` (http://localhost:8501) se visualizan 3 noticias, 3 instituciones y 3 categorías antes de aplicar filtros, como pide la guía.")
fig(CAP / "oes-01-tablero-inicial-3-3-3.jpg", "Tablero local inicial: 3 noticias, 3 instituciones y 3 categorías (registros DEMO) — Paso 6.")
fig(WEB / "web-01-inicio-panorama.jpg", "Aplicación pública: inicio y panorama con los 7 registros.")
fig(WEB / "web-03-matriz-marketing.jpg", "Aplicación pública: matriz institución × tema (enfoque de marketing, solo noticias verificadas).")

# ============ 7 ============
h1("7. Incorporación responsable de fuentes reales (Paso 7)")
p("**Método.** Para cada noticia se copiaron manualmente título, institución, categoría, fecha, URL directa a la nota y un resumen propio, y se cargaron con `agregar_noticia.py --csv datos/noticias_univ.csv`. Agentes de IA abrieron cada URL y comprobaron que titular y fecha coincidieran con el enlace; por eso el verificador figura como agente de IA y **las noticias requieren confirmación humana del grupo**. No se extrajo masivamente ningún sitio.")
tabla([["Institución", "Fecha", "Categoría", "Tema", "Asunto"],
 ["UNDC", "2026-10-23", "Universidad pública", "Admisión y captación", "Inicio del ciclo ordinario CEPRE 2026-II"],
 ["PUCP", "2026-10-16", "Universidad privada", "Imagen institucional y eventos", "Aula Magna 2026"],
 ["PUCP", "2026-10-30", "Universidad privada", "Investigación e innovación", "Vivienda contra heladas con la Universidad Nacional de Juliaca"],
 ["PUCP", "2026-11-06", "Universidad privada", "Imagen institucional y eventos", "Doctorado honoris causa a Mircea Cărtărescu"]], [2.2, 2.4, 3.2, 4.0, 4.2])
p("**Limitación de gob.pe.** Los portales gob.pe (MINEDU, SUNEDU, PRONABEC, CONCYTEC) bloquearon el acceso automatizado (HTTP 418, «Acceso restringido»). No se eludió el bloqueo; por ello no hay noticias reales de entes rectores o reguladores. Queda como tarea del grupo registrarlas a mano con `agregar_noticia.py`.")
p("**Lectura de la matriz.** La PUCP concentra su comunicación en imagen institucional y eventos, y la UNDC comunica admisión. Con cuatro noticias reales no se puede generalizar: es una observación descriptiva sobre una muestra mínima y no aleatoria.")
fig(CAP / "oes-10-matriz-institucion-tema.jpg", "Matriz institución × tema con las noticias cargadas.")

# ============ 8 ============
h1("8. Validación: pruebas de laboratorio P1–P6")
p("Las seis pruebas de la guía se ejecutaron sobre el prototipo. Además, la suite automática pytest (tests/test_oes.py) aprobó 13 de 13 pruebas.")
tabla([["Prueba", "Procedimiento (guía)", "Resultado esperado (guía)", "Resultado obtenido", "Evidencia"],
 ["P1", "Ejecutar carga dos veces", "No se duplican las 3 URLs", "✓ Tras dos cargas la base tiene 3 filas y 3 URL distintas.", "oes-02 (texto); Figura 2 (oes-01)"],
 ["P2", "Filtrar Universidad pública", "Se muestra UNMSM (dato didáctico)", "✓ Solo aparece UNMSM.", "Figura 6 (oes-03)"],
 ["P3", "Buscar PUCP", "Una fila en resultados", "✓ Una fila de PUCP (con los datos DEMO).", "Figura 7 (oes-04)"],
 ["P4", "Buscar término inexistente", "0 noticias y aviso sin error", "✓ 0 noticias y aviso «No hay resultados con esos filtros», sin error.", "Figura 8 (oes-05)"],
 ["P5", "Exportar CSV", "Archivo abre con encabezados y filas filtradas", "✓ CSV UTF-8 con encabezados y solo las filas filtradas.", "oes-06 (CSV)"],
 ["P6", "Agregar una noticia real verificada", "Aumenta contador y se conserva URL directa", "✓ De 3 a 7 noticias, 4 verificadas, URL directa conservada; una segunda carga las marca como duplicadas.", "oes-07 (texto); Figuras 9 y 10 (oes-08, oes-09)"]], [1.3, 3.0, 3.2, 5.2, 3.3])
fig(CAP / "oes-03-P2-filtro-universidad-publica.jpg", "P2. Filtro «Universidad pública»: solo se muestra UNMSM.")
fig(CAP / "oes-04-P3-busqueda-PUCP.jpg", "P3. Búsqueda «PUCP»: una fila en resultados.")
fig(CAP / "oes-05-P4-termino-inexistente.jpg", "P4. Término inexistente: 0 noticias y aviso, sin error.")
fig(CAP / "oes-08-P6-nota-original-UNDC.jpg", "P6. Nota original de la UNDC abierta desde la URL directa guardada, usada para contrastar titular y fecha.")
fig(CAP / "oes-09-tablero-final-7-noticias.jpg", "P6. Tablero final con 7 noticias (3 DEMO y 4 reales verificadas).")
h2("Evidencia textual (extractos)")
p("**P1 (oes-02-P1-carga-doble.txt):**")
code(leer(CAP / "oes-02-P1-carga-doble.txt"))
p("**P5 (oes-06-P5-oes_resultados.csv), encabezados y filas exportadas (columnas principales):**")
csvl = leer(CAP / "oes-06-P5-oes_resultados.csv").splitlines()
code("\n".join(l if len(l) < 150 else l[:147] + "..." for l in csvl))
p("**P6 (oes-07-P6-carga-noticias-reales.txt), resumen de las dos cargas:**")
t7 = [l for l in leer(CAP / "oes-07-P6-carga-noticias-reales.txt").splitlines() if l.startswith(("===", "Antes", "Resumen", "---", "Despues", "Después"))]
code("\n".join(t7))

# ============ 9 ============
h1("9. Actividades de ampliación por niveles")
p("**Nivel básico (obligatorio):** cumplido; ver la tabla de cumplimiento.")
p("**Nivel intermedio (opcional): lo que se adelantó.**")
li("Campo `fecha_captura` (fecha de registro de cada noticia).")
li("Campo `verificado_por` (quién verificó) y `estado_verificacion` (Ejemplo didáctico, Verificada o Pendiente), con la regla de que «Verificada» exige verificador.")
li("Filtro por rango de fechas y por estado de verificación en la aplicación.")
p("**Nivel intermedio: lo que quedó pendiente.** Normalizar instituciones y fuentes en tablas separadas (solo se propuso el modelo) y generar un informe PDF automático desde la aplicación (este informe se entrega en formato Word).")
p("**Nivel avanzado (proyecto futuro):** no se implementó. Quedan módulos de transparencia presupuestal y calidad, alertas por palabras clave, resúmenes asistidos por IA con revisión humana y registro de cambios normativos.")

# ============ 10 ============
h1("10. Preguntas para discusión y reflexión")
p("**(a) ¿En qué se diferencia un portal de noticias de un observatorio con análisis prospectivo?** Un portal agrega y ordena publicaciones cronológicamente; su valor es el acceso. Un observatorio añade criterios de selección explícitos, clasificación estable, series comparables en el tiempo y metodología documentada, de modo que se puedan identificar patrones. El análisis prospectivo va más allá: usa esas series para plantear escenarios y tendencias (por ejemplo, cambios regulatorios o de oferta de becas) y declara sus supuestos e incertidumbre. Este prototipo es un observatorio descriptivo; no hace prospectiva.")
p("**(b) ¿Qué riesgos introduce una noticia sin fecha o sin URL directa?** Sin fecha no se puede ordenar, filtrar por periodo ni saber si la información sigue vigente (una convocatoria cerrada puede parecer abierta). Sin URL directa no se puede auditar el origen, otra persona no puede reproducir la verificación, un enlace a la portada cambia con el tiempo y se pierde la deduplicación por URL. Por eso el prototipo rechaza ambos casos.")
p("**(c) ¿Por qué un conteo de noticias no demuestra calidad universitaria?** El número de noticias refleja el volumen de comunicación, que depende del tamaño del área de prensa, la estrategia de marketing y la presencia digital, no de la calidad de la enseñanza o la investigación. Además, la muestra depende de las fuentes elegidas (sesgo de selección) y no distingue entre noticia sustantiva y publicidad. La calidad requiere indicadores validados: licenciamiento, acreditación, producción científica y empleabilidad, entre otros.")
p("**(d) ¿Qué indicadores serían necesarios para estudiar ejecución presupuestal y regulación?** Para ejecución presupuestal: PIM (presupuesto institucional modificado), devengado y porcentaje de avance respecto al PIM, por institución y año, de Consulta Amigable del MEF. Para regulación y calidad: estado de licenciamiento institucional y de programas (SUNEDU), acreditación de programas (SINEACE) y producción científica de docentes registrados (RENACYT, CONCYTEC). Son datos estructurados con fuente oficial y periodicidad propia; no se obtienen de noticias, por lo que requerirían nuevas entidades en el modelo y otra forma de carga.")
p("**(e) ¿Cómo se verificaría un resumen generado con inteligencia artificial?** (1) Abrir la URL directa y leer la nota original. (2) Comparar cada afirmación del resumen (cifras, nombres, fechas, plazos) con el texto fuente. (3) Comprobar que fecha y titular coinciden con la publicación. (4) Descartar frases ausentes en la fuente (alucinaciones) o que cambien el sentido. (5) Reescribir con palabras propias lo dudoso. (6) Registrar quién verificó y marcar «Verificada» solo tras esta revisión humana; mientras tanto, «Pendiente».")

# ============ 11 ============
h1("11. Análisis crítico, ética y conclusiones")
h2("11.1 Análisis crítico y ética")
li("**Fuentes oficiales y revisión manual.** Se priorizan sitios institucionales; cada registro se contrasta con la nota original.")
li("**robots.txt y términos de uso.** Antes de capturar automáticamente de un sitio se debe revisar su robots.txt y sus condiciones. El prototipo no implementa extracción automática. Cuando gob.pe rechazó el acceso automatizado (HTTP 418), no se intentó eludir el bloqueo.")
li("**No extracción masiva.** Se registran pocas notas, con título, fecha, URL y resumen propio; no se copian textos completos ni se sobrecargan los servidores.")
li("**Registros DEMO marcados.** Los 3 registros de la guía llevan el estado «Ejemplo didáctico» y la aplicación advierte que no son noticias verificadas.")
li("**Verificación por IA.** Los registros verificados por agentes de IA requieren confirmación humana del grupo antes de considerarse definitivos. El código, las pruebas y las evidencias se produjeron con un equipo de agentes de IA coordinados por un orquestador, y el grupo responde por el contenido final.")
li("**Límites del prototipo.** Muestra pequeña y no aleatoria; una sola tabla; clasificación temática manual y subjetiva; sin actualización automática; sin medición de calidad ni de impacto; sin análisis prospectivo.")
li("**Datos personales.** No se recolectan datos personales; solo información institucional publicada. Conviene usar un nombre de grupo o iniciales en verificado_por.")
h2("11.2 Conclusiones")
li("El prototipo cumple el objetivo de registrar, clasificar, consultar y visualizar novedades con trazabilidad de fuente, fecha, captura y verificación: las seis pruebas P1–P6 resultaron satisfactorias y la suite automática aprobó 13 de 13 pruebas.")
li("La validación en la entrada (fecha, URL directa, marcadores, duplicados) y las restricciones de la base evitaron los errores frecuentes de la guía original; en P1 y P6 las cargas repetidas no generaron duplicados y fueron informadas como tales.")
li("El campo tema y la matriz institución × tema permiten una lectura de marketing educativo, pero describen el mensaje publicado, no la calidad ni el impacto, y con cuatro noticias reales no se puede generalizar.")
li("La verificación humana sigue siendo indispensable, y no hay noticias reales de entes (MINEDU, SUNEDU, PRONABEC, CONCYTEC) porque gob.pe bloqueó el acceso automatizado.")
li("Como mejora futura se propone normalizar el modelo en Institución, Fuente y Noticia, incorporar indicadores oficiales (PIM/devengado, licenciamiento, acreditación, RENACYT) y evaluar capturas automatizadas respetando robots.txt y los términos de uso.")

# ============ 12 ============
h1("12. Publicación")
p("La aplicación se publicó en Streamlit Community Cloud (Python 3.11, sin secrets) y el código en un repositorio público de GitHub, configurado con el correo noreply de GitHub para no exponer datos personales.")
p("**Aplicación pública (solo lectura):** " + APP)
p("**Repositorio:** " + REPO)
p("En la web pública el formulario Registrar aparece en «Modo solo lectura». Si se define una clave `clave_registro` en los secrets, el registro se exige siempre, incluso en la nube. La aplicación en la nube no guarda altas (el disco no es persistente): las noticias se cargan en local y se sube el archivo oes.db actualizado. Tras un periodo sin visitas la aplicación se «duerme» y tarda unos segundos en reactivarse.")
fig(WEB / "web-08-repositorio-github.jpg", "Repositorio público en GitHub.")

# ============ Referencias ============
h1("Referencias")
REFS = [
 "Consejo Nacional de Ciencia, Tecnología e Innovación Tecnológica. (s. f.). *Página institucional*. Gobierno del Perú. https://www.gob.pe/concytec",
 "Ministerio de Educación. (s. f.). *Página institucional*. Gobierno del Perú. https://www.gob.pe/minedu",
 "Observatorio de Educación Superior. (2026a). *Portal institucional*. Recuperado el 12 de noviembre de 2026, de https://observatorio.com.pe/",
 "Observatorio de Educación Superior. (2026b). *Reporte de monitoreo con corte al 7 de noviembre de 2026* [Documento PDF proporcionado por la docente para análisis académico].",
 "Programa Nacional de Becas y Crédito Educativo. (s. f.). *Página institucional*. Gobierno del Perú. https://www.gob.pe/pronabec",
 "Python Software Foundation. (2026). *sqlite3 — DB-API 2.0 interface for SQLite databases* (Python 3.11). https://docs.python.org/3.11/library/sqlite3.html",
 "Streamlit Inc. (s. f.). *Streamlit documentation*. https://docs.streamlit.io/",
 "Superintendencia Nacional de Educación Superior Universitaria. (s. f.). *Página institucional*. Gobierno del Perú. https://www.gob.pe/sunedu",
]
for r in REFS: B.append(("ref", r))

# ============ Anexo ============
h1("Anexo. Correcciones y observaciones a la guía")
tabla([["N.°", "Problema detectado", "Corrección aplicada"],
 ["1", "El subtítulo «El marketing en la educación» no tenía desarrollo.", "Se agregó el campo tema y la matriz institución × tema."],
 ["2", "La Figura 1 de la guía mostraba Instituciones/Fuentes/Noticias, pero se implementa una sola tabla.", "Nuevo diagrama que distingue lo implementado de lo propuesto."],
 ["3", "«Categoría» contiene el tipo de institución.", "Se mantiene por compatibilidad con P2 y se añade tema como clasificación temática."],
 ["4", "RF01 «Registrar noticia» no tenía interfaz.", "Formulario Registrar y script agregar_noticia.py."],
 ["5", "El Paso 7 usaba la ruta relativa oes.db, que crea una base vacía si se ejecuta desde otra carpeta.", "Ruta absoluta y variable de entorno OES_DB."],
 ["6", "El marcador https://URL-DIRECTA-DE-LA-NOTA podía insertarse por error y INSERT OR IGNORE ocultaba duplicados.", "Validación que rechaza marcadores e informa duplicados."],
 ["7", "use_container_width está obsoleto en Streamlit reciente.", "Se usa width=\"stretch\"."],
 ["8", "La fecha sin validar (texto libre) rompe el orden.", "CHECK en SQLite y validación AAAA-MM-DD."],
 ["9", "En PowerShell la activación del entorno puede bloquearse; el comando python del equipo era 3.8.", "Nota Set-ExecutionPolicy -Scope CurrentUser RemoteSigned; se usó py -3.11."],
 ["10", "Versiones sin fijar y altair ausente de las dependencias.", "requirements.txt con versiones fijas e incluyendo altair."],
 ["11", "Trazabilidad básica sin fecha de captura ni verificador.", "Campos fecha_captura, verificado_por y estado_verificacion."],
 ["12", "P6 no era reproducible entre grupos.", "Se guarda la URL directa y la captura de la nota original."]], [1.2, 8.0, 6.8])

# ---------------- DOCX ----------------
doc = Document()
for s in doc.sections:
    s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.5)
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(6)
for n, sz in (("Heading 1", 15), ("Heading 2", 13), ("Title", 22)):
    hs = doc.styles[n]; hs.font.name = "Calibri"; hs.font.size = Pt(sz); hs.font.bold = True
    hs.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    hs.element.rPr.rFonts.set(qn("w:ascii"), "Calibri"); hs.element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")

TOK = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")
def runs(par, text, size=None, bold=False):
    for part in TOK.split(text):
        if not part: continue
        if part.startswith("**"): r = par.add_run(part[2:-2]); r.bold = True
        elif part.startswith("`"):
            r = par.add_run(part[1:-1]); r.font.name = "Consolas"
        elif part.startswith("*"): r = par.add_run(part[1:-1]); r.italic = True
        else: r = par.add_run(part)
        if bold: r.bold = True
        if size: r.font.size = Pt(size)

def borders(tbl):
    tblPr = tbl._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        x = OxmlElement(f"w:{e}")
        x.set(qn("w:val"), "single"); x.set(qn("w:sz"), "4"); x.set(qn("w:color"), "808080")
        b.append(x)
    tblPr.append(b)

def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), color); tcPr.append(sh)

# Caratula
for _ in range(3): doc.add_paragraph()
t = doc.add_paragraph(TITULO, style="Title"); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
for txt, bd in (("Práctica Guiada N.° 08 — Informe de cumplimiento del laboratorio", True),
                ("Universidad Nacional de Cañete (UNDC)", False),
                ("Curso: Inteligencia Artificial aplicada al Marketing Digital", False),
                ("Integrantes: " + INTEGRANTES, False), ("Fecha: 13 de noviembre de 2026", False),
                ("Prototipo académico con Python, SQLite y Streamlit", False),
                ("Aplicación pública: " + APP, False), ("Repositorio: " + REPO, False)):
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = q.add_run(txt); r.bold = bd; r.font.size = Pt(14 if bd else 11)
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

nfig = 0
for blk in B:
    k = blk[0]
    if k == "h1": doc.add_heading(blk[1], 1)
    elif k == "h2": doc.add_heading(blk[1], 2)
    elif k == "pb": doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    elif k == "p":
        q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; runs(q, blk[1])
    elif k == "li":
        q = doc.add_paragraph(style="List Bullet"); runs(q, blk[1])
    elif k == "code":
        for ln in blk[1].split("\n"):
            q = doc.add_paragraph(); q.paragraph_format.space_after = Pt(0)
            q.paragraph_format.left_indent = Cm(0.5)
            r = q.add_run(ln); r.font.name = "Consolas"; r.font.size = Pt(8.5)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
    elif k == "ref":
        q = doc.add_paragraph(); runs(q, blk[1])
        q.paragraph_format.left_indent = Cm(1.27); q.paragraph_format.first_line_indent = Cm(-1.27)
    elif k == "t":
        rows, widths = blk[1], blk[2]
        tb = doc.add_table(rows=len(rows), cols=len(rows[0])); tb.alignment = WD_TABLE_ALIGNMENT.CENTER
        tb.autofit = False; borders(tb)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                c = tb.cell(i, j)
                if widths: c.width = Cm(widths[j])
                par = c.paragraphs[0]; par.paragraph_format.space_after = Pt(2)
                runs(par, val, size=9.5, bold=(i == 0))
                if i == 0: shade(c, "D9E2F3")
                if val == "✓": par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()
    elif k == "f":
        _, path, w, cap = blk
        nfig += 1
        q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        q.paragraph_format.keep_with_next = True
        q.add_run().add_picture(str(path), width=Cm(w))
        c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.add_run(f"Figura {nfig}. {cap}"); r.italic = True; r.font.size = Pt(10)

out = BASE / "Informe_Laboratorio_Practica08.docx"
doc.save(out)
print("OK", out, "figuras:", nfig)
