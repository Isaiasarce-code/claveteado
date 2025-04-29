import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Mi App", page_icon="📊", menu_items={
    'Get Help': None,
    'Report a bug': None,
    'About': None
})

st.set_page_config(layout="wide")
# Estilo personalizado: fondo rojo y texto blanco
st.markdown("""
    <style>
        body {
            background-color: #FF6F61;  /* Rojo oscuro */
            color: white;
        }
        .stApp {
            background-color: #FF6F61;
            color: white;
        }
        .css-18ni7ap.e8zbici2 {  /* Títulos y textos */
            color: white;
        }
        .css-1v0mbdj.edgvbvh3 {  /* Textos de widget */
            color: white;
        }
        .st-bb {
            background-color: #FF6F61;
        }
        .st-cm, .st-cn {
            color: white;
        }
        .css-1cpxqw2.edgvbvh3 { /* Texto de subheader */
            color: white;
        }
        .css-qrbaxs.e16nr0p34 { /* Tabla */
            background-color: white !important;
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)

# Estilo personalizado (tu CSS)
st.markdown("""
    <style>
        /* aquí va tu CSS... */
    </style>
""", unsafe_allow_html=True)

# Logo arriba a la derecha
st.markdown("""
    <div style="display: flex; justify-content: flex-end;">
        <img src="https://www.promotoriadeseguros.com.mx/wp-content/uploads/2021/09/logoanaseguros-1024x609.png" 
             alt="Logo ANA Seguros" width="200" style="margin-top: -60px; margin-right: 10px;">
    </div>
""", unsafe_allow_html=True)

# Título de la app
st.title("CLAVETEADO DE UNIDADES ANA SEGUROS")

# Subida del archivo de consultas (solo este lo sube el usuario)
st.subheader("Carga el archivo de consultas")
archivo_consultas = st.file_uploader("", type=["csv"])

# Cargar catálogo automáticamente desde GitHub
url_catalogo = "https://raw.githubusercontent.com/Isaiasarce-code/claveteado/main/CATALOGO.csv"
df_catalogo = pd.read_csv(url_catalogo, encoding='latin1')


#url_catalogo = "https://raw.githubusercontent.com/Isaiasarce-code/claveteado/blob/main/CATALOGO.csv"
#df_catalogo = pd.read_csv(url_catalogo, encoding='latin1')

if archivo_consultas:
    # Cargar archivo de consultas
    df_consultas = pd.read_csv(archivo_consultas, encoding='latin1')

    # Convertir columnas relevantes a mayúsculas
    columnas_consulta = ["MARCA", "DESCRIPCION1", "AÑO", "TRANSMISION", "MODELO"]
    for col in columnas_consulta:
        df_consultas[col] = df_consultas[col].astype(str).str.upper().str.strip()

    # Definir columnas relevantes
    col_exacto = "MARCA"
    col_fuzzy = "DESCRIPCION1"
    col_numero = "AÑO"
    col_transmision = "TRANSMISION"
    col_modelo = "DESCRIPCION2"

    columnas_catalogo = [col_exacto, col_fuzzy, col_numero, col_transmision, col_modelo]
    for col in columnas_catalogo:
        df_catalogo[col] = df_catalogo[col].astype(str)

    umbral_fuzzy = 0
    resultados_ordenados = []

    progreso = st.progress(0)
    total_filas = len(df_consultas)

    for i, fila in df_consultas.iterrows():
        valor_marca = str(fila["MARCA"])
        valor_descripcion = str(fila["DESCRIPCION1"])
        valor_ano = str(fila["AÑO"])
        valor_transmision = str(fila["TRANSMISION"])
        valor_modelo = str(fila["MODELO"])

        filtro1 = df_catalogo[col_exacto].str.contains(valor_marca, na=False, case=False)
        filtro3 = df_catalogo[col_numero].str.contains(valor_ano, na=False, case=False)
        filtro4 = df_catalogo[col_transmision].str.contains(valor_transmision, na=False, case=False)
        filtro5 = df_catalogo[col_modelo].str.contains(valor_modelo, na=False, case=False)

        df_filtrado_parcial = df_catalogo[filtro1 & filtro3 & filtro4 & filtro5].copy()

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
            color: black; /* Cambia el color del texto a negro */
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
