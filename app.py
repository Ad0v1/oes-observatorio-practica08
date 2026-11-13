"""Dashboard del Observatorio de Educación Superior (OES) — prototipo académico."""
import hmac
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

import oes_db

st.set_page_config(page_title="OES — Prototipo académico", layout="wide")

st.title("Observatorio de Educación Superior — Prototipo académico")
st.caption(
    "Los registros marcados como «Ejemplo didáctico» son ilustrativos y no "
    "constituyen información verificada."
)

# --- Lectura de datos (nunca se crea la base desde aquí) ---
df = pd.DataFrame()
if oes_db.ruta_db().exists():
    df = oes_db.leer_noticias()
if df.empty:
    st.warning("No hay noticias. Ejecute preparar_datos.py")
    st.stop()

df["fecha"] = df["fecha"].astype(str)
fechas = pd.to_datetime(df["fecha"], errors="coerce").dropna()
f_min, f_max = fechas.min().date(), fechas.max().date()

# --- Barra lateral: filtros ---
st.sidebar.header("Filtros")
categorias_disp = sorted(df["categoria"].dropna().unique())
estados_disp = sorted(df["estado_verificacion"].dropna().unique())

sel_cat = st.sidebar.multiselect(
    "Categoría", categorias_disp, default=categorias_disp, key="f_categoria"
)
sel_estado = st.sidebar.multiselect(
    "Estado de verificación", estados_disp, default=estados_disp, key="f_estado"
)
rango = st.sidebar.date_input("Rango de fechas", value=(f_min, f_max), key="f_fechas")
texto = st.sidebar.text_input("Buscar título o institución", key="f_busqueda")

# Tolerar que el usuario elija una sola fecha (rango incompleto)
if isinstance(rango, (tuple, list)):
    if len(rango) == 2:
        desde, hasta = rango
    elif len(rango) == 1:
        desde, hasta = rango[0], f_max
    else:
        desde, hasta = f_min, f_max
else:
    desde, hasta = rango, f_max

fil = oes_db.filtrar(
    df, categorias=sel_cat, texto=texto, estados=sel_estado, desde=desde, hasta=hasta
)


def _barras(serie):
    d = serie.rename_axis("etiqueta").reset_index(name="noticias")
    return alt.Chart(d).mark_bar().encode(
        x=alt.X("etiqueta:N", sort="-y", title=None,
                axis=alt.Axis(labelAngle=-30, labelLimit=0)),
        y=alt.Y("noticias:Q", title="Noticias"),
        tooltip=["etiqueta", "noticias"],
    )


# --- Métricas ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Noticias", len(fil))
c2.metric("Instituciones", fil["institucion"].nunique() if len(fil) else 0)
c3.metric("Categorías", fil["categoria"].nunique() if len(fil) else 0)
c4.metric(
    "Verificadas",
    int((fil["estado_verificacion"] == "Verificada").sum()) if len(fil) else 0,
)

tab_pan, tab_not, tab_reg, tab_met = st.tabs(
    ["Panorama", "Noticias", "Registrar", "Metodología"]
)

# --- Panorama ---
with tab_pan:
    if fil.empty:
        st.info("No hay resultados con esos filtros")
    else:
        st.subheader("Noticias por categoría")
        st.altair_chart(_barras(fil["categoria"].value_counts()), width="stretch")
        st.subheader("Noticias por tema")
        st.altair_chart(_barras(fil["tema"].value_counts()), width="stretch")
        st.subheader("Matriz institución × tema (enfoque de marketing)")
        ver = fil[fil["estado_verificacion"] == "Verificada"]
        if len(ver) > 0:
            base_m = ver
            st.caption("Matriz calculada solo con noticias en estado Verificada.")
        else:
            base_m = fil
            st.caption(
                "No hay noticias verificadas en este filtro: la matriz incluye "
                "ejemplos didácticos."
            )
        st.caption(
            "La matriz describe qué comunica cada institución; no mide calidad."
        )
        matriz = pd.crosstab(base_m["institucion"], base_m["tema"])
        _m = matriz.reset_index().melt(
            id_vars=matriz.index.name or "institucion", var_name="tema",
            value_name="noticias",
        )
        _m.columns = ["institucion", "tema", "noticias"]
        st.altair_chart(
            alt.Chart(_m).mark_bar().encode(
                x=alt.X("institucion:N", sort="-y", title=None,
                        axis=alt.Axis(labelAngle=-30, labelLimit=0)),
                y=alt.Y("noticias:Q", title="Noticias"),
                color=alt.Color("tema:N", title="Tema"),
                tooltip=["institucion", "tema", "noticias"],
            ),
            width="stretch",
        )
        st.dataframe(matriz, width="stretch")

# --- Noticias ---
with tab_not:
    if fil.empty:
        st.info("No hay resultados con esos filtros")
    else:
        columnas = ["fecha", "institucion", "categoria", "tema", "titulo",
                    "fuente", "estado_verificacion", "url"]
        st.dataframe(
            fil[columnas],
            width="stretch",
            hide_index=True,
            column_config={
                "url": st.column_config.LinkColumn("url", display_text="Abrir nota")
            },
        )
        st.download_button(
            "Exportar CSV",
            data=oes_db.a_csv(fil),
            file_name="oes_resultados.csv",
            mime="text/csv",
        )

# --- Registrar (protegido) ---
def _registro_habilitado() -> tuple[bool, str]:
    """Si existe la clave en secrets, siempre se exige; si no, solo se permite en local."""
    try:
        clave = st.secrets["clave_registro"]
    except Exception:
        clave = None
    if clave is None:
        try:
            host = st.context.headers.get("host", "")
        except Exception:
            host = ""
        if host.startswith("localhost") or host.startswith("127.0.0.1"):
            return True, ""
        return False, "Modo solo lectura"
    ingresada = st.text_input("Clave de registro", type="password", key="f_clave")
    if ingresada and hmac.compare_digest(ingresada, str(clave)):
        return True, ""
    return False, "Ingrese la clave de registro para habilitar el formulario."


with tab_reg:
    habilitado, aviso = _registro_habilitado()
    if not habilitado:
        st.info(aviso)
    else:
        with st.form("form_registro", clear_on_submit=False):
            titulo = st.text_input("Título")
            institucion = st.text_input("Institución")
            categoria = st.selectbox("Categoría", oes_db.CATEGORIAS)
            fuente = st.text_input("Fuente")
            fecha = st.date_input("Fecha de publicación", value=date.today())
            url = st.text_input("URL directa de la nota")
            resumen = st.text_area("Resumen (redacción propia)")
            tema = st.selectbox("Tema", oes_db.TEMAS, index=len(oes_db.TEMAS) - 1)
            estado = st.selectbox("Estado de verificación", oes_db.ESTADOS, index=2)
            verificado_por = st.text_input("Verificado por (obligatorio si es Verificada)")
            enviar = st.form_submit_button("Registrar noticia")
        if enviar:
            ok, msg = oes_db.insertar_noticia({
                "titulo": titulo, "institucion": institucion, "categoria": categoria,
                "fuente": fuente, "fecha": fecha.isoformat(), "url": url,
                "resumen": resumen, "tema": tema, "estado_verificacion": estado,
                "verificado_por": verificado_por or None,
            })
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# --- Metodología ---
with tab_met:
    st.markdown(
        """
**Fuentes.** Las noticias provienen de los sitios y comunicados oficiales de entes
rectores, entes reguladores y universidades.

**Verificación.** Cada registro se contrasta manualmente con su URL directa antes de
marcarse como «Verificada», indicando quién lo verificó. Los estados son
«Verificada», «Pendiente» y «Ejemplo didáctico».

**Registros DEMO.** Los tres registros iniciales están marcados como
«Ejemplo didáctico» y no deben citarse como evidencia.

**Alcance.** Este prototipo académico no reproduce el OES comercial.

**Límites.** Un conteo de noticias no mide calidad ni impacto de la comunicación
institucional; la matriz institución × tema solo describe la frecuencia de lo
registrado.
"""
    )
