import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

# Título de la app
st.title("Filtro y Coincidencia de Datos")

# Subida de archivos
st.subheader("Carga los archivos CSV")
archivo_catalogo = st.file_uploader("Sube el archivo del catálogo", type=["csv"])
archivo_consultas = st.file_uploader("Sube el archivo de consultas", type=["csv"])

if archivo_catalogo and archivo_consultas:
    # Cargar los archivos
    df_catalogo = pd.read_csv(archivo_catalogo, encoding='latin1')
    df_consultas = pd.read_csv(archivo_consultas, encoding='latin1')

    # Convertir las columnas relevantes a mayúsculas y manejar valores nulos
    columnas_consulta = ["MARCA", "DESCRIPCION1", "AÑO", "TRANSMISION", "MODELO"]
    for col in columnas_consulta:
        if col in df_consultas.columns:
            df_consultas[col] = df_consultas[col].fillna('').astype(str).str.upper().str.strip()

    # Definir las columnas a usar del catálogo
    col_exacto = "MARCA"
    col_fuzzy = "DESCRIPCION1"
    col_numero = "AÑO"
    col_transmision = "TRANSMISION"
    col_modelo = "DESCRIPCION2"

    # Convertir las columnas del catálogo a string y manejar valores nulos
    columnas_catalogo = [col_exacto, col_fuzzy, col_numero, col_transmision, col_modelo]
    for col in columnas_catalogo:
        df_catalogo[col] = df_catalogo[col].fillna('').astype(str).str.upper().str.strip()

    # Parámetro para coincidencia fuzzy
    umbral_fuzzy = 0

    # Lista para almacenar resultados
    resultados_ordenados = []

    # Barra de progreso
    progreso = st.progress(0)
    total_filas = len(df_consultas)

    # Iterar sobre todas las filas del archivo de CONSULTA
    for i, fila in df_consultas.iterrows():
        valor_marca = fila["MARCA"]
        valor_descripcion = fila["DESCRIPCION1"]
        valor_ano = fila["AÑO"]
        valor_transmision = fila["TRANSMISION"]
        valor_modelo = fila["MODELO"]

        # Empezamos con todo el catálogo
        df_filtrado_parcial = df_catalogo.copy()

        # Aplicar filtros SOLO si la celda NO está vacía (pero dejando pasar las vacías)
        if valor_marca.strip():
            df_filtrado_parcial = df_filtrado_parcial[df_filtrado_parcial[col_exacto].str.contains(valor_marca, na=False, case=False, regex=False)]
        if valor_ano.strip():
            df_filtrado_parcial = df_filtrado_parcial[df_filtrado_parcial[col_numero].str.contains(valor_ano, na=False, case=False, regex=False)]
        if valor_transmision.strip():
            df_filtrado_parcial = df_filtrado_parcial[df_filtrado_parcial[col_transmision].str.contains(valor_transmision, na=False, case=False, regex=False)]
        if valor_modelo.strip():
            df_filtrado_parcial = df_filtrado_parcial[df_filtrado_parcial[col_modelo].str.contains(valor_modelo, na=False, case=False, regex=False)]

        if not df_filtrado_parcial.empty:
            # Coincidencia fuzzy en "DESCRIPCION1"
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

        # Actualizar barra de progreso
        progreso.progress((i + 1) / total_filas)

    # Convertir resultados en DataFrame
    df_final = pd.DataFrame(resultados_ordenados)

    # Mostrar los resultados
    st.subheader("Resultados del Filtrado")
    st.dataframe(df_final)

    # Botón para descargar el archivo resultante
    st.subheader("Descarga el Resultado")
    csv_resultado = df_final.to_csv(index=False, encoding='latin1')
    st.download_button(
        label="Descargar CSV",
        data=csv_resultado,
        file_name="RESULTADO_FILTRADO.csv",
        mime="text/csv"
    )

    st.success("Proceso completado con éxito.")
