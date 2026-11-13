# -*- coding: utf-8 -*-
"""Genera informe/arquitectura.png (arquitectura del OES)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

W, H = 12.0, 8.2
fig, ax = plt.subplots(figsize=(W, H), dpi=150)
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
fig.patch.set_facecolor("white")

IMP = dict(fc="#DCEBFA", ec="#1F5A94", ls="-", lw=1.8)
PRO = dict(fc="#FFF4D6", ec="#B7791F", ls=(0, (4, 3)), lw=1.6)


def caja(x, y, w, h, titulo, lineas, est, tsize=10.5, lsize=8.3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=est["fc"], ec=est["ec"], ls=est["ls"], lw=est["lw"]))
    ax.text(x + w / 2, y + h - 0.2, titulo, ha="center", va="top", fontsize=tsize,
            fontweight="bold", color="#14283C")
    ax.text(x + w / 2, y + h - 0.55, "\n".join(lineas), ha="center", va="top",
            fontsize=lsize, color="#222", linespacing=1.35)


def flecha(x1, y1, x2, y2, dash=False):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", lw=2, color="#444",
                                ls="--" if dash else "-"))


ax.text(W / 2, H - 0.3, "Arquitectura del Observatorio de Educación Superior (OES)",
        ha="center", va="center", fontsize=15, fontweight="bold", color="#14283C")
ax.text(W / 2, H - 0.68, "Flujo: fuente → captura → validación → almacenamiento → consulta → decisiones",
        ha="center", va="center", fontsize=10, color="#555")

# Fila superior: 1 -> 2 -> 3
y1, h1 = 4.55, 2.55
caja(0.3, y1, 3.4, h1, "1. Fuentes oficiales",
     ["MINEDU", "SUNEDU", "PRONABEC", "CONCYTEC", "Universidades", "(portales públicos)"], IMP)
caja(4.3, y1, 3.4, h1, "2. Captura controlada",
     ["Revisión manual, nota por nota", "agregar_noticia.py", "(CLI / carga desde CSV)",
      "Formulario «Registrar»", "(local o con clave)"], IMP)
caja(8.3, y1, 3.4, h1, "3. Validación",
     ["oes_db.validar_noticia:", "campos obligatorios", "fecha AAAA-MM-DD no futura",
      "URL directa; rechazo de marcadores", "duplicados (URL única)", "estado de verificación"], IMP)
flecha(3.72, y1 + h1 / 2, 4.28, y1 + h1 / 2)
flecha(7.72, y1 + h1 / 2, 8.28, y1 + h1 / 2)

# Fila inferior: 4 -> 5 -> 6
y2, h2 = 1.75, 2.35
caja(8.3, y2, 3.4, h2, "4. Almacenamiento",
     ["SQLite  oes.db", "tabla «noticias» (desnormalizada)", "tema, estado_verificacion,",
      "fecha_captura, verificado_por"], IMP)
caja(4.3, y2, 3.4, h2, "5. Consulta  (app.py, Streamlit)",
     ["Filtros: categoría, estado,", "fechas y texto; métricas", "Gráficos por categoría y tema",
      "Matriz institución × tema", "Exportación CSV"], IMP, tsize=10)
caja(0.3, y2, 3.4, h2, "6. Decisiones / salidas",
     ["Dashboard", "Archivos CSV", "Informe"], IMP)
flecha(10.0, y1 - 0.02, 10.0, y2 + h2 + 0.02)
flecha(8.28, y2 + h2 / 2, 7.72, y2 + h2 / 2)
flecha(4.28, y2 + h2 / 2, 3.72, y2 + h2 / 2)

# Propuestos
yp, hp = 0.2, 1.1
props = [
    (0.3, "Normalización", ["Institución / Fuente"]),
    (2.6, "Alertas", ["por palabras clave"]),
    (4.9, "Resúmenes con IA", ["con revisión humana"]),
    (7.2, "Transparencia/calidad", ["módulos propuestos"]),
    (9.5, "Captura RSS / API", ["automatizada"]),
]
for x, t, l in props:
    caja(x, yp, 2.1, hp, t, l, PRO, tsize=9, lsize=8)
ax.text(0.3, 1.5, "Extensiones propuestas (no implementadas)", ha="left", fontsize=9,
        style="italic", color="#8A5A00")

ax.legend(handles=[
    Patch(fc=IMP["fc"], ec=IMP["ec"], lw=1.8, label="Implementado"),
    Patch(fc=PRO["fc"], ec=PRO["ec"], lw=1.6, ls="--", label="Propuesto / no implementado")],
    loc="lower right", bbox_to_anchor=(0.98, 0.16), fontsize=9, frameon=True, ncol=2)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arquitectura.png")
fig.savefig(out, dpi=150, facecolor="white")
print(out)
