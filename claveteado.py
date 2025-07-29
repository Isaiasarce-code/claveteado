import streamlit as st
import pandas as pd
import re
from rapidfuzz import process, fuzz

st.set_page_config(layout="wide")

# Estilo personalizado
st.markdown("""
    <style>
        body {
            background-color: #FF6F61;
            color: white;
        }
        .stApp {
            background-color: #FF6F61;
            color: white;
        }
        .css-18ni7ap.e8zbici2,
        .css-1v0mbdj.edgvbvh3,
        .st-cm, .st-cn,
        .css-1cpxqw2.edgvbvh3 {
            color: white;
        }
        .css-qrbaxs.e16nr0p34 {
            background-color: white !important;
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)

# Logo superior derecho
st.markdown("""
    <div style="display: flex; justify-content: flex-end;">
        <img src="https://www.promotoriadeseguros.com.mx/wp-content/uploads/2021/09/logoanaseguros-1024x609.png"
             alt="Logo ANA Seguros" width="200" style="margin-top: -60px; margin-right: 10px;">
    </div>
""", unsafe_allow_html=True)

st.title("CLAVETEADO DE UNIDADES ANA SEGUROS")

# Subida del archivo de consultas
st.subheader("Carga el archivo de consultas")
archivo_consultas = st.file_uploader("", type=["csv"])

# Cargar catálogo desde GitHub
url_catalogo = "https://raw.githubusercontent.com/Isaiasarce-code/claveteado/main/CATALOGO.csv"
df_catalogo = pd.read_csv(url_catalogo, encoding='latin1')

# Limpieza básica del catálogo
columnas_catalogo = ["MARCA", "DESCRIPCION1", "AÑO", "TRANSMISION", "DESCRIPCION2"]
for col in columnas_catalogo:
    df_catalogo[col] = df_catalogo[col].fillna("").astype(str).str.upper().str.strip()

if archivo_consultas:
    df_consultas = pd.read_csv(archivo_consultas, encoding='latin1')
    columnas_consulta = ["MARCA", "DESCRIPCION1", "AÑO", "TRANSMISION", "MODELO"]
    for col in columnas_consulta:
        df_consultas[col] = df_consultas[col].fillna("").astype(str).str.upper().str.strip()

    col_exacto = "MARCA"
    col_fuzzy = "DESCRIPCION1"
    col_numero = "AÑO"
    col_transmision = "TRANSMISION"
    col_modelo = "DESCRIPCION2"
    umbral_fuzzy = 0

    resultados_ordenados = []
    progreso = st.progress(0)
    total_filas = len(df_consultas)

    for i, fila in df_consultas.iterrows():
        valor_marca = fila["MARCA"]
        valor_descripcion = fila["DESCRIPCION1"]
        valor_ano = fila["AÑO"]
        valor_transmision = fila["TRANSMISION"]
        valor_modelo = fila["MODELO"]

        if not valor_descripcion:
            resultados_ordenados.append({
                "MARCA": valor_marca,
                "DESCRIPCION": valor_descripcion,
                "AÑO": valor_ano,
                "MODELO": valor_modelo,
                "TRANSMISION": valor_transmision,
                "MENSAJE": "DESCRIPCION1 vacía, se requiere para comparar."
            })
            progreso.progress((i + 1) / total_filas)
            continue

        filtros = []
        if valor_marca:
            filtros.append(df_catalogo[col_exacto].str.contains(re.escape(valor_marca), na=False, case=False))
        if valor_ano:
            filtros.append(df_catalogo[col_numero].str.contains(re.escape(valor_ano), na=False, case=False))
        if valor_transmision:
            filtros.append(df_catalogo[col_transmision].str.contains(re.escape(valor_transmision), na=False, case=False))
        if valor_modelo:
            filtros.append(df_catalogo[col_modelo].str.contains(re.escape(valor_modelo), na=False, case=False))

        if filtros:
            filtro_total = filtros[0]
            for f in filtros[1:]:
                filtro_total &= f
            df_filtrado_parcial = df_catalogo[filtro_total].copy()
        else:
            df_filtrado_parcial = df_catalogo.copy()

        if not df_filtrado_parcial.empty:
            mejor_coincidencia, score, idx = process.extractOne(
                valor_descripcion,
                df_filtrado_parcial[col_fuzzy],
                scorer=fuzz.partial_ratio
            )

            if score >= umbral_fuzzy:
                df_filtrado = df_filtrado_parcial.loc[[idx]].copy()
                resultados_ordenados.append(df_filtrado.iloc[0].to_dict())
            else:
                resultados_ordenados.append({
                    "MARCA": valor_marca,
                    "DESCRIPCION": valor_descripcion,
                    "AÑO": valor_ano,
                    "MODELO": valor_modelo,
                    "TRANSMISION": valor_transmision,
                    "MENSAJE": "No se encontró coincidencia fuzzy con el umbral requerido."
                })
        else:
            resultados_ordenados.append({
                "MARCA": valor_marca,
                "DESCRIPCION": valor_descripcion,
                "AÑO": valor_ano,
                "MODELO": valor_modelo,
                "TRANSMISION": valor_transmision,
                "MENSAJE": "No se encontraron registros que cumplan los filtros."
            })

        progreso.progress((i + 1) / total_filas)

    df_final = pd.DataFrame(resultados_ordenados)

    st.subheader("Resultados del Filtrado")
    st.dataframe(df_final)

    st.subheader("Descarga el Resultado")
    csv_resultado = df_final.to_csv(index=False, encoding='latin1')

    st.markdown("""
        <style>
            div[data-testid="stDownloadButton"] {
                color: black;
            }
        </style>
    """, unsafe_allow_html=True)

    st.download_button(
        label="Descargar CSV",
        data=csv_resultado,
        file_name="RESULTADO_FILTRADO.csv",
        mime="text/csv"
    )

    st.success("Proceso completado con éxito.")
