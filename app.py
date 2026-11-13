"""Dashboard del Observatorio de Educación Superior (OES) — prototipo académico."""
import hmac
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

import oes_db

st.set_page_config(page_title="OES — Prototipo académico", layout="wide")

st.title("Observatorio de Educación Superior — Prototipo académico")
st.caption("UNDC · Inteligencia Artificial aplicada al Marketing Digital · Práctica 08")
st.caption(
    "Los registros marcados como «Ejemplo didáctico» son ilustrativos y no "
    "constituyen información verificada."
)

# --- Lectura de datos (nunca se crea la base desde aquí) ---
@st.cache_data(ttl=300)
def cargar_noticias(ruta: str, mtime: int) -> pd.DataFrame:
    """Lectura en caché; la ruta y la fecha de modificación forman parte de la clave."""
    return oes_db.leer_noticias()


df = pd.DataFrame()
_ruta = oes_db.ruta_db()
if _ruta.exists():
    df = cargar_noticias(str(_ruta), _ruta.stat().st_mtime_ns).copy()
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
solo_ver = st.sidebar.toggle(
    "Solo noticias verificadas", key="f_solo_verificadas", value=False
)
rango = st.sidebar.date_input(
    "Rango de fechas", value=(f_min, f_max), key="f_fechas", format="DD/MM/YYYY"
)
texto = st.sidebar.text_input("Buscar título o institución", key="f_busqueda")


def _restablecer():
    st.session_state["f_categoria"] = list(categorias_disp)
    st.session_state["f_estado"] = list(estados_disp)
    st.session_state["f_solo_verificadas"] = False
    st.session_state["f_fechas"] = (f_min, f_max)
    st.session_state["f_busqueda"] = ""


st.sidebar.button("Restablecer filtros", on_click=_restablecer)
_cap = pd.to_datetime(df["fecha_captura"], errors="coerce").max()
_cap_txt = _cap.strftime("%d/%m/%Y") if pd.notna(_cap) else "—"
st.sidebar.caption(f"Base actualizada al {_cap_txt} · {len(df)} registros en total")

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
if solo_ver:
    fil = fil[fil["estado_verificacion"] == "Verificada"]


_PALETA = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442"]
_TEMAS = list(oes_db.TEMAS)
_COLORES = [_PALETA[i] if i < len(_PALETA) else "#7F7F7F" for i in range(len(_TEMAS))]
_COLORES[_TEMAS.index("Sin tema")] = "#7F7F7F"


def _color_tema(titulo="Tema"):
    return alt.Color(
        "tema:N", title=titulo,
        scale=alt.Scale(domain=_TEMAS, range=_COLORES),
        legend=alt.Legend(orient="bottom", labelLimit=0, columns=2, titleLimit=0),
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

if len(fil):
    _ult = pd.to_datetime(fil["fecha"], errors="coerce").max()
    _pct = 100 * (fil["estado_verificacion"] == "Verificada").mean()
    _ult_txt = _ult.strftime("%d/%m/%Y") if pd.notna(_ult) else "—"
    st.caption(f"Última noticia: {_ult_txt} · {_pct:.0f} % verificadas")

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
                color=_color_tema(),
                tooltip=["institucion", "tema", "noticias"],
            ),
            width="stretch",
        )
        st.dataframe(matriz, width="stretch")

        # --- Línea de tiempo ---
        st.subheader("Línea de tiempo de noticias")
        _t = fil.copy()
        _t["_f"] = pd.to_datetime(_t["fecha"], errors="coerce")
        _t = _t.dropna(subset=["_f"])
        if len(_t):
            _dias = (_t["_f"].max() - _t["_f"].min()).days
            if _dias >= 28:
                _t["periodo"] = _t["_f"].dt.to_period("W").dt.start_time
                _tit = "Semana (inicio)"
            else:
                _t["periodo"] = _t["_f"].dt.normalize()
                _tit = "Día"
            _g = _t.groupby(["periodo", "institucion"]).size().reset_index(name="noticias")
            st.altair_chart(
                alt.Chart(_g).mark_bar().encode(
                    x=alt.X("periodo:T", title=_tit, axis=alt.Axis(format="%d/%m")),
                    y=alt.Y("noticias:Q", title="Noticias"),
                    color=alt.Color(
                        "institucion:N", title="Institución",
                        scale=alt.Scale(range=_PALETA + ["#000000", "#999999"]),
                        legend=alt.Legend(orient="bottom", labelLimit=0, titleLimit=0),
                    ),
                    tooltip=["periodo:T", "institucion", "noticias"],
                ),
                width="stretch",
            )

        # --- Perfil por institución ---
        st.subheader("Perfil de institución")
        _insts = sorted(fil["institucion"].dropna().unique())
        _sel = st.selectbox("Perfil de institución", _insts, key="f_perfil")
        _p = fil[fil["institucion"] == _sel]
        _pf = pd.to_datetime(_p["fecha"], errors="coerce")
        _pc1, _pc2, _pc3 = st.columns(3)
        _pc1.metric("Noticias de la institución", len(_p))
        _pc2.metric(
            "% verificadas",
            f"{100 * (_p['estado_verificacion'] == 'Verificada').mean():.0f} %",
        )
        _pc3.metric(
            "Última noticia",
            _pf.max().strftime("%d/%m/%Y") if pd.notna(_pf.max()) else "—",
        )
        _mt = _p["tema"].value_counts().rename_axis("tema").reset_index(name="noticias")
        st.altair_chart(
            alt.Chart(_mt).mark_bar().encode(
                y=alt.Y("tema:N", sort="-x", title=None,
                        axis=alt.Axis(labelLimit=0)),
                x=alt.X("noticias:Q", title="Noticias",
                        axis=alt.Axis(tickMinStep=1, format="d")),
                color=_color_tema(),
                tooltip=[alt.Tooltip("tema:N", title="Tema"),
                         alt.Tooltip("noticias:Q", title="Cantidad")],
            ),
            width="stretch",
        )
        st.markdown("**Últimas 3 noticias**")
        for _, _r in _p.assign(_f=_pf).sort_values("_f", ascending=False).head(3).iterrows():
            _fx = _r["_f"].strftime("%d/%m/%Y") if pd.notna(_r["_f"]) else _r["fecha"]
            st.markdown(f"- {_fx} · {_r['titulo']} — [Abrir nota]({_r['url']})")

# --- Noticias ---
with tab_not:
    if fil.empty:
        st.info("No hay resultados con esos filtros")
    else:
        base = fil.reset_index(drop=True)
        vista = base[["fecha", "institucion", "tema", "titulo",
                      "estado_verificacion", "url"]].copy()
        vista["fecha"] = pd.to_datetime(vista["fecha"], errors="coerce")
        evento = st.dataframe(
            vista,
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="t_noticias",
            column_config={
                "fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
                "institucion": "Institución",
                "tema": "Tema",
                "titulo": st.column_config.TextColumn("Título", width="large"),
                "estado_verificacion": "Estado",
                "url": st.column_config.LinkColumn("Nota", display_text="Abrir nota"),
            },
        )
        filas = evento.selection.rows if evento is not None else []
        if filas and filas[0] < len(base):
            r = base.iloc[filas[0]]
            _f = pd.to_datetime(r["fecha"], errors="coerce")
            _c = pd.to_datetime(r["fecha_captura"], errors="coerce")
            with st.container(border=True):
                st.subheader(str(r["titulo"]))
                st.markdown(
                    f"**Institución:** {r['institucion']}  \n"
                    f"**Categoría:** {r['categoria']}  \n"
                    f"**Tema:** {r['tema']}  \n"
                    f"**Fuente:** {r['fuente']}  \n"
                    f"**Fecha:** {_f.strftime('%d/%m/%Y') if pd.notna(_f) else r['fecha']}  \n"
                    f"**Estado:** {r['estado_verificacion']}  \n"
                    f"**Verificado por:** {r['verificado_por'] or '—'}  \n"
                    f"**Fecha de captura:** {_c.strftime('%d/%m/%Y') if pd.notna(_c) else r['fecha_captura']}"
                )
                st.write(str(r["resumen"]))
                st.link_button("Abrir nota", str(r["url"]))
        else:
            st.caption("Seleccione una fila para ver el detalle.")
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
            fecha = st.date_input("Fecha de publicación", value=date.today(), format="DD/MM/YYYY")
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
                cargar_noticias.clear()
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

# --- Pie ---
st.divider()
st.caption(
    "Prototipo académico, no es el OES comercial. Repositorio: "
    "[github.com/Ad0v1/oes-observatorio-practica08]"
    "(https://github.com/Ad0v1/oes-observatorio-practica08)"
)
