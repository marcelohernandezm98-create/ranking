import streamlit as st
from datetime import time

st.set_page_config(page_title="Ranking Jefes SAC", page_icon="📈")

st.title("🏆 Calculador de Ranking SAC")

# --- DICCIONARIOS DE CONFIGURACIÓN ---
ARQUETIPOS = {
    "E": 500,
    "D": 1000,
    "C": 2000,
    "B": 4000,
    "A": 10000
}

# --- SELECCIÓN DE PERFIL ---
perfil = st.sidebar.selectbox("Perfil del Colaborador", ["Jefe SAC Mixto", "Jefe SAC Entrega", "Jefe SAC APT"])
nombre = st.sidebar.text_input("Nombre del Colaborador", "Empleado 1")

# --- FUNCIONES DE CÁLCULO REVISADAS ---
def calc_puntos_tiempo(valor_ingresado, hora_excelente, hora_tolerable):
    # Comparamos objetos de tipo datetime.time
    if valor_ingresado <= hora_excelente:
        return 10
    elif valor_ingresado <= hora_tolerable:
        return 5
    else:
        return 2

# --- FORMULARIO ---
with st.form("calculadora"):
    st.subheader(f"Evaluación: {perfil}")
    puntos_totales = 0
    
    if perfil == "Jefe SAC Mixto":
        # Línea corregida: Uso de objetos time explícitos
        t_salida = st.time_input("Hora Salida de Rutas (Meta 7:30)", time(7, 30))
        pts_salida = calc_puntos_tiempo(t_salida, time(7, 30), time(8, 0))
        
        t_visita = st.time_input("Hora Visita 1er Cliente (Meta 8:30)", time(8, 30))
        pts_visita = calc_puntos_tiempo(t_visita, time(8, 30), time(9, 0))
        
        val_fill = st.number_input("Fill Rate (%)", 0.0, 100.0, 98.0)
        pts_fill = 25 if val_fill >= 98 else (15 if val_fill >= 97 else 10)
        
        val_prox = st.number_input("Proximidad (%)", 0.0, 100.0, 98.0)
        pts_prox = 10 if val_prox >= 98 else (7 if val_prox >= 97 else 5)
        
        st.write("**Inventario por Arquetipo**")
        col_arq, col_monto = st.columns(2)
        arq = col_arq.selectbox("Tipo de CEDI", list(ARQUETIPOS.keys()))
        monto_inv = col_monto.number_input("Monto Diferencia Real $", min_value=0.0)
        # Lógica solicitada: <= meta gana 25 pts (en Mixto), si no 0.
        pts_inv = 25 if monto_inv <= ARQUETIPOS[arq] else 0
        
        val_merma = st.number_input("Merma CEDI", 0.0, 10.0, 0.05, format="%.3f")
        pts_merma = 10 if val_merma <= 0.05 else (5 if val_merma <= 0.10 else 0)
        
        rotura = st.radio("Rotura de Garrafón", ["En Objetivo", "Fuera de Objetivo"])
        pts_rotura = 10 if rotura == "En Objetivo" else 0
        
        puntos_totales = pts_salida + pts_visita + pts_fill + pts_prox + pts_inv + pts_merma + pts_rotura

    elif perfil == "Jefe SAC APT":
        val_oos = st.number_input("OOS %", 0.0, 100.0, 0.05, format="%.3f")
        pts_oos = 20 if val_oos <= 0.05 else (10 if val_oos <= 0.10 else 0)
        
        col_arq, col_monto = st.columns(2)
        arq = col_arq.selectbox("Tipo de CEDI", list(ARQUETIPOS.keys()))
        monto_inv = col_monto.number_input("Monto Diferencia Real $", min_value=0.0)
        # En APT la ponderación de inventario es 40 pts
        pts_inv = 40 if monto_inv <= ARQUETIPOS[arq] else 0
        
        val_merma = st.number_input("Merma CEDI", 0.0, 10.0, 0.05)
        pts_merma = 20 if val_merma <= 0.05 else 10
        
        rotura = st.radio("Rotura de Garrafón", ["En Objetivo", "Fuera de Objetivo"])
        pts_rotura = 20 if rotura == "En Objetivo" else 0
        
        puntos_totales = pts_oos + pts_inv + pts_merma + pts_rotura

    # Agregamos lógica para "Jefe SAC Entrega" para evitar errores si se selecciona
    elif perfil == "Jefe SAC Entrega":
        st.info("Configurando rubros de Entrega...")
        # (Aquí podrías replicar los campos de Salida/Visita/Fill/Prox con sus pesos de 20/20/40/20)

    boton = st.form_submit_button("Calcular Ranking")

if boton:
    st.success(f"### Puntaje Total de {nombre}: {puntos_totales} / 100")
    if puntos_totales == 100:
        st.balloons()