import streamlit as st
import pandas as pd
from datetime import time, datetime
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ranking SAC Pro", layout="centered", page_icon="🏆")

# --- BASE DE DATOS LOCAL (CSV) ---
DB_FILE = "historial_ranking.csv"

# --- CONSTANTES ---
MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
ARQUETIPOS = {"E": 500, "D": 1000, "C": 2000, "B": 4000, "A": 10000}

def guardar_datos(datos):
    df_nuevo = pd.DataFrame([datos])
    if not os.path.isfile(DB_FILE):
        df_nuevo.to_csv(DB_FILE, index=False)
    else:
        df_nuevo.to_csv(DB_FILE, mode='a', header=False, index=False)

# --- BARRA LATERAL ---
st.sidebar.markdown(
    """
    <div style='text-align: center; font-size: 60px; font-weight: bold; color: #4169E1; line-height: 1.2;'>
        SAC
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    <div style='text-align: center; font-style: italic; font-size: 14px; margin-bottom: 30px; color: #555;'>
        “Servicio no es solo entregar el producto, es dar confianza, respeto y soluciones”
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Menú Principal")
menu = st.sidebar.radio("Ir a:", ["📝 Registrar Evaluación", "🏆 Ver Rankings"])

# ==========================================
# LÓGICA DE CÁLCULO
# ==========================================
def calcular_visita_base(hora):
    if hora <= time(8, 30): return 10
    elif hora <= time(9, 0): return 5
    elif hora <= time(10, 0): return 2
    else: return 0

def calcular_salida_base(hora):
    if hora <= time(7, 30): return 10
    elif hora <= time(8, 0): return 5
    elif hora <= time(9, 0): return 2
    else: return 0

def calcular_rango_porcentajes(valor, max_pts, mid_pts):
    if valor <= 0.05: return max_pts
    elif valor <= 0.10: return mid_pts
    else: return 0

# ==========================================
# SECCIÓN 1: REGISTRO
# ==========================================
if menu == "📝 Registrar Evaluación":
    st.title("Nueva Evaluación")
    
    # --- DATOS GENERALES ---
    st.subheader("Datos del Colaborador")
    col1, col2 = st.columns(2)
    perfil = col1.selectbox("Perfil", [
        "Jefe SAC Mixto", "Jefe SAC Entrega", "JT Mixto", "Jefe SAC APT", 
        "JT Garrafón", "Jefe/Sup APT Garrafón/embotellado", "Jefe/Sup APT Embotellado"
    ])
    nombre = col2.text_input("Nombre Completo")
    
    col3, col4 = st.columns(2)
    cedis = col3.text_input("CEDIS")
    zona = col4.text_input("Zona")

    st.subheader("Periodo a Evaluar")
    c_mes, c_ano = st.columns(2)
    mes_actual_idx = datetime.now().month - 1
    mes_eval = c_mes.selectbox("Mes", MESES, index=mes_actual_idx)
    ano_eval = c_ano.number_input("Año", min_value=2024, max_value=2030, value=datetime.now().year)

    st.markdown("---")

    with st.form("form_eval"):
        pts_totales = 0
        desglose_txt = "" 
        
        # --- LÓGICA DE PERFILES ---
        if perfil == "Jefe SAC Mixto":
            st.info("Configuración Mixto: Salida(10), Visita(10), FillRate(25), Prox(10), Inv(25), Merma(10), Rotura(10)")
            t_salida = st.time_input("Salida de Rutas", time(7, 30), step=60)
            pts_s = calcular_salida_base(t_salida)
            t_visita = st.time_input("Visita 1er Cliente", time(8, 30), step=60)
            pts_v = calcular_visita_base(t_visita)
            fr = st.number_input("Fill Rate %", 0.0, 100.0, 98.0, step=0.1)
            pts_fr = 25 if fr >= 98 else (15 if fr >= 97 else (5 if fr >= 96 else 0))
            pr = st.number_input("Proximidad %", 0.0, 100.0, 98.0, step=0.1)
            pts_pr = 10 if pr >= 98 else (7 if pr >= 97 else (5 if pr >= 96 else 0))
            c1, c2 = st.columns(2)
            arq = c1.selectbox("Arquetipo CEDI", list(ARQUETIPOS.keys()))
            monto = c2.number_input("Diferencia Inventario $", 0.0)
            pts_inv = 25 if monto <= ARQUETIPOS[arq] else 0
            merma = st.number_input("Merma CEDI", 0.0, 1.0, 0.05, format="%.3f")
            pts_merma = calcular_rango_porcentajes(merma, 10, 5)
            rotura = st.radio("Rotura Garrafón", ["En Objetivo", "Fuera de Objetivo"])
            pts_rot = 10 if rotura == "En Objetivo" else 0
            
            pts_totales = pts_s + pts_v + pts_fr + pts_pr + pts_inv + pts_merma + pts_rot
            desglose_txt = f"Salida:{pts_s} | Visita:{pts_v} | FR:{pts_fr} | Prox:{pts_pr} | Inv:{pts_inv} | Merma:{pts_merma} | Rot:{pts_rot}"

        elif perfil == "Jefe SAC Entrega" or perfil == "JT Mixto":
            st.info(f"Configuración {perfil}: Pesos Altos.")
            c1, c2 = st.columns(2)
            t_salida = c1.time_input("Salida de Rutas", time(7, 30), step=60)
            pts_s = calcular_salida_base(t_salida) * 2
            t_visita = c2.time_input("Visita 1er Cliente", time(8, 30), step=60)
            pts_v = calcular_visita_base(t_visita) * 2
            fr = c1.number_input("Fill Rate % (Emb)", 0.0, 100.0, 98.0, step=0.1)
            pts_fr = 40 if fr >= 98 else (24 if fr >= 97 else (8 if fr >= 96 else 0))
            pr = c2.number_input("Proximidad %", 0.0, 100.0, 98.0, step=0.1)
            pts_pr = 20 if pr >= 98 else (12 if pr >= 97 else (4 if pr >= 96 else 0))
            
            pts_totales = pts_s + pts_v + pts_fr + pts_pr
            desglose_txt = f"Salida:{pts_s} | Visita:{pts_v} | FR:{pts_fr} | Prox:{pts_pr}"

        elif perfil == "Jefe SAC APT":
            st.info("Configuración APT Original.")
            oos = st.number_input("OOS %", 0.0, 1.0, 0.05, format="%.3f")
            pts_oos = calcular_rango_porcentajes(oos, 20, 10)
            c1, c2 = st.columns(2)
            arq = c1.selectbox("Arquetipo CEDI", list(ARQUETIPOS.keys()))
            monto = c2.number_input("Diferencia Inventario $", 0.0)
            pts_inv = 40 if monto <= ARQUETIPOS[arq] else 0
            merma = st.number_input("Merma CEDI", 0.0, 1.0, 0.05)
            pts_merma = calcular_rango_porcentajes(merma, 20, 10)
            rotura = st.radio("Rotura Garrafón", ["En Objetivo", "Fuera de Objetivo"])
            pts_rot = 20 if rotura == "En Objetivo" else 0
            
            pts_totales = pts_oos + pts_inv + pts_merma + pts_rot
            desglose_txt = f"OOS:{pts_oos} | Inv:{pts_inv} | Merma:{pts_merma} | Rot:{pts_rot}"

        elif perfil == "JT Garrafón":
            st.info("Configuración JT Garrafón.")
            c1, c2 = st.columns(2)
            t_salida = c1.time_input("Salida de Rutas", time(7, 30), step=60)
            pts_s = calcular_salida_base(t_salida) * 1.5
            t_visita = c2.time_input("Visita 1er Cliente", time(8, 30), step=60)
            pts_v = calcular_visita_base(t_visita) * 1.5
            ep = c1.number_input("Entrega Perfecta %", 0.0, 100.0, 98.0, step=0.1)
            pts_ep = 40 if ep >= 98 else (20 if ep >= 97 else (5 if ep >= 95 else 0))
            pr = c2.number_input("Proximidad %", 0.0, 100.0, 98.0, step=0.1)
            pts_pr = 10 if pr >= 98 else (7 if pr >= 97 else (5 if pr >= 96 else 0))
            falseo = st.number_input("Falseo (Cantidad)", min_value=0, step=1)
            pts_fal = 20 if falseo < 4 else (10 if falseo <= 7 else 0)
            
            pts_totales = pts_s + pts_v + pts_ep + pts_pr + pts_fal
            desglose_txt = f"Salida:{pts_s} | Visita:{pts_v} | E.Perf:{pts_ep} | Prox:{pts_pr} | Falseo:{pts_fal}"

        elif perfil == "Jefe/Sup APT Garrafón/embotellado":
            st.info("Configuración APT Mixto.")
            oos = st.number_input("OOS %", 0.0, 1.0, 0.05, format="%.3f")
            pts_oos = calcular_rango_porcentajes(oos, 20, 10) 
            c1, c2 = st.columns(2)
            arq = c1.selectbox("Arquetipo CEDI", list(ARQUETIPOS.keys()))
            monto = c2.number_input("Diferencia Inventario $", 0.0)
            pts_inv = 30 if monto <= ARQUETIPOS[arq] else 0
            merma = st.number_input("Merma CEDI", 0.0, 1.0, 0.05, format="%.3f")
            pts_merma = calcular_rango_porcentajes(merma, 20, 10)
            rotura = st.radio("Rotura Garrafón", ["En Objetivo", "Fuera de Objetivo"])
            pts_rot = 20 if rotura == "En Objetivo" else 0
            t_salida = st.time_input("Salida de Rutas", time(7, 30), step=60)
            pts_salida = calcular_salida_base(t_salida)
            
            pts_totales = pts_oos + pts_inv + pts_merma + pts_rot + pts_salida
            desglose_txt = f"OOS:{pts_oos} | Inv:{pts_inv} | Merma:{pts_merma} | Rot:{pts_rot} | Salida:{pts_salida}"

        elif perfil == "Jefe/Sup APT Embotellado":
            st.info("Configuración APT Embotellado.")
            oos = st.number_input("OOS %", 0.0, 1.0, 0.05, format="%.3f")
            pts_oos = calcular_rango_porcentajes(oos, 25, 12)
            c1, c2 = st.columns(2)
            arq = c1.selectbox("Arquetipo CEDI", list(ARQUETIPOS.keys()))
            monto = c2.number_input("Diferencia Inventario $", 0.0)
            pts_inv = 40 if monto <= ARQUETIPOS[arq] else 0
            merma = st.number_input("Merma CEDI", 0.0, 1.0, 0.05, format="%.3f")
            pts_merma = calcular_rango_porcentajes(merma, 25, 12)
            t_salida = st.time_input("Salida de Rutas", time(7, 30), step=60)
            pts_salida = calcular_salida_base(t_salida)
            
            pts_totales = pts_oos + pts_inv + pts_merma + pts_salida
            desglose_txt = f"OOS:{pts_oos} | Inv:{pts_inv} | Merma:{pts_merma} | Salida:{pts_salida}"

        enviar = st.form_submit_button("💾 Guardar Evaluación")

    if enviar:
        if nombre:
            datos = {
                "Mes": mes_eval,
                "Año": ano_eval,
                "Nombre": nombre,
                "CEDIS": cedis,
                "Zona": zona,
                "Perfil": perfil,
                "Puntaje Total": pts_totales,
                "Desglose": desglose_txt, 
                "Fecha Reg": str(datetime.now().date())
            }
            guardar_datos(datos)
            st.success(f"✅ Registrado: {nombre} | {mes_eval} {ano_eval} | Puntos: {pts_totales}")
            if pts_totales >= 95: st.balloons()
        else:
            st.error("⚠️ Falta el nombre del colaborador.")

# ==========================================
# SECCIÓN 2: RANKINGS
# ==========================================
elif menu == "🏆 Ver Rankings":
    st.title("Tablero de Posiciones")

    if os.path.isfile(DB_FILE):
        df = pd.read_csv(DB_FILE)
        
        # --- CORRECCIÓN AUTOMÁTICA ---
        columnas_faltantes = ["Mes", "Año", "CEDIS", "Zona", "Desglose"]
        for col in columnas_faltantes:
            if col not in df.columns:
                df[col] = "Sin detalles previos"
        
        if "Puntaje" in df.columns and "Puntaje Total" not in df.columns:
            df.rename(columns={"Puntaje": "Puntaje Total"}, inplace=True)
            df.to_csv(DB_FILE, index=False)

        # --- FILTROS GLOBALES ---
        col_f1, col_f2 = st.columns(2)
        filtro_ano = col_f1.selectbox("Filtrar Año", df["Año"].unique())
        df = df[df["Año"] == filtro_ano]

        # --- PESTAÑAS ---
        tab1, tab2 = st.tabs(["📅 Ranking Mensual", "📆 Acumulado Anual"])

        # >>> TAB 1: RANKING MENSUAL <<<
        with tab1:
            mes_sel = st.selectbox("Selecciona Mes", MESES)
            df_mes = df[df["Mes"] == mes_sel]

            if not df_mes.empty:
                st.markdown(f"### 🏆 Mejores de {mes_sel} {filtro_ano}")
                df_sorted = df_mes.sort_values(by="Puntaje Total", ascending=False).reset_index(drop=True)

                for i, row in df_sorted.iterrows():
                    rank = i + 1
                    icono = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
                    
                    with st.container():
                        c1, c2, c3 = st.columns([1, 4, 2])
                        c1.markdown(f"## {icono}")
                        c2.markdown(f"**{row['Nombre']}**")
                        c2.caption(f"{row['Perfil']} | {row['CEDIS']} - {row['Zona']}")
                        c2.markdown(f"**🔍 Detalle:** `{row['Desglose']}`")
                        c3.metric("Puntos", f"{row['Puntaje Total']:.1f}")
                        st.divider()
            else:
                st.info(f"No hay evaluaciones registradas para {mes_sel} del {filtro_ano}.")

        # >>> TAB 2: ACUMULADO ANUAL <<<
        with tab2:
            st.markdown(f"### 📈 Desempeño Anual {filtro_ano} (Promedio)")
            st.caption("Promedio de puntos totales.")
            
            if not df.empty:
                df_anual = df.groupby(["Nombre", "Perfil", "CEDIS", "Zona"])["Puntaje Total"].mean().reset_index()
                df_anual = df_anual.sort_values(by="Puntaje Total", ascending=False).reset_index(drop=True)

                for i, row in df_anual.iterrows():
                    rank = i + 1
                    icono = "👑" if rank == 1 else "⭐" if rank <= 3 else f"#{rank}"
                    
                    with st.container():
                        c1, c2, c3 = st.columns([1, 4, 2])
                        c1.markdown(f"## {icono}")
                        c2.markdown(f"**{row['Nombre']}**")
                        c2.caption(f"Promedio Anual | {row['CEDIS']}")
                        c3.metric("Promedio", f"{row['Puntaje Total']:.1f}")
                        st.divider()
            else:
                st.info("No hay datos en este año para calcular el acumulado.")

        # --- ZONA DE DESCARGA SEGURA ---
        st.markdown("---")
        st.markdown("### 🔐 Área Gerencia Nacional")
        st.caption("Ingrese la contraseña para descargar la base de datos completa.")
        
        password = st.text_input("Contraseña:", type="password")
        
        # AQUÍ SE DEFINE LA CONTRASEÑA
        if password == "SAC2026":
            @st.cache_data
            def convert_df(df): return df.to_csv(index=False).encode('utf-8')
            
            st.success("✅ Acceso Concedido")
            st.download_button("📥 Descargar Base Completa", convert_df(df), "ranking_sac_completo.csv", "text/csv")
        elif password:
            st.error("🚫 Contraseña incorrecta")

    else:
        st.info("Aún no hay datos registrados.")
