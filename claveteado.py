import pandas as pd
from rapidfuzz import process, fuzz
#definitivo hasta este momento
# Cargar los archivos
ruta_catalogo = "/content/CATALOGO.csv"
df_catalogo = pd.read_csv(ruta_catalogo, encoding='latin1')

ruta_consultas = "/content/CONSULTA.csv"
df_consultas = pd.read_csv(ruta_consultas, encoding='latin1')

# Convertir todas las columnas relevantes de CONSULTA a mayúsculas para asegurar coincidencias correctas
df_consultas["MARCA"] = df_consultas["MARCA"].astype(str).str.upper().str.strip()
df_consultas["DESCRIPCION1"] = df_consultas["DESCRIPCION1"].astype(str).str.upper().str.strip()
df_consultas["AÑO"] = df_consultas["AÑO"].astype(str).str.upper().str.strip()
df_consultas["TRANSMISION"] = df_consultas["TRANSMISION"].astype(str).str.upper().str.strip()
df_consultas["MODELO"] = df_consultas["MODELO"].astype(str).str.upper().str.strip()


# Definir las columnas a usar del catálogo
col_exacto = "MARCA"       # Filtro exacto
col_fuzzy = "DESCRIPCION1" # Filtro fuzzy
col_numero = "AÑO"         # Filtro con str.contains
col_transmision = "TRANSMISION" #filtro con str contains
col_modelo = "DESCRIPCION2"   #filtro con str contains

# Convertir las columnas a string para evitar problemas de tipo
df_catalogo[col_exacto] = df_catalogo[col_exacto].astype(str)
df_catalogo[col_fuzzy] = df_catalogo[col_fuzzy].astype(str)
df_catalogo[col_numero] = df_catalogo[col_numero].astype(str)
df_catalogo[col_transmision] = df_catalogo[col_transmision].astype(str)
df_catalogo[col_modelo] = df_catalogo[col_modelo].astype(str)

# Definir un umbral para la coincidencia fuzzy
umbral_fuzzy = 0

# Lista para almacenar resultados manteniendo el orden original
resultados_ordenados = []

# Iterar sobre todas las filas del archivo de CONSULTA
for _, fila in df_consultas.iterrows():
    valor_marca = str(fila["MARCA"])
    valor_descripcion = str(fila["DESCRIPCION1"])
    valor_ano = str(fila["AÑO"])
    valor_transmision = str(fila["TRANSMISION"])
    valor_modelo = str(fila["MODELO"])

    # Filtro 1: Coincidencia exacta en "MARCA"
    filtro1 = df_catalogo[col_exacto] == valor_marca

    # Filtro 3: Coincidencia en "AÑO" usando str.contains
    filtro3 = df_catalogo[col_numero].str.contains(valor_ano, na=False)
    filtro4 = df_catalogo[col_transmision].str.contains(valor_transmision, na=False)
    filtro5 = df_catalogo[col_modelo].str.contains(valor_modelo, na=False)

    # Aplicar los filtros exactos para reducir el catálogo
    df_filtrado_parcial = df_catalogo[filtro1 & filtro3 & filtro4 & filtro5].copy()

    if not df_filtrado_parcial.empty:
        # Filtro 2: Coincidencia fuzzy en "DESCRIPCION1"
        mejor_coincidencia, score, idx = process.extractOne(
            valor_descripcion,
            df_filtrado_parcial[col_fuzzy],
            scorer=fuzz.partial_ratio
        )
        print(f"Mejor coincidencia para {valor_descripcion}: {mejor_coincidencia}, Score: {score}")

        if score >= umbral_fuzzy:
            df_filtrado = df_filtrado_parcial.loc[[idx]].copy()
            resultados_ordenados.append(df_filtrado.iloc[0].to_dict())  # Se guarda como diccionario
        else:
            print("No se encontró una coincidencia fuzzy con el umbral requerido.")
            resultados_ordenados.append({
                "MARCA": valor_marca,
                "DESCRIPCION": valor_descripcion,
                "AÑO": valor_ano,
                "MODELO": valor_modelo,
                "TRANSMISION": valor_transmision,
                "MENSAJE": "No se encontró coincidencia fuzzy con el umbral requerido."
            })
    else:
        print("No se encontraron registros que cumplan los filtros exactos y de año4.")
        resultados_ordenados.append({
            "MARCA": valor_marca,
            "DESCRIPCION": valor_descripcion,
            "AÑO": valor_ano,
            "MODELO": valor_modelo,
            "TRANSMISION": valor_transmision,
            "MENSAJE": "No se encontraron registros que cumplan los filtros exactos y de año2."
        })

# Convertir la lista de resultados ordenados en un DataFrame
df_final = pd.DataFrame(resultados_ordenados)

# Guardar el resultado en un archivo CSV respetando el orden original
df_final.to_csv("/content/RESULTADO_FILTRADO.csv", index=False, encoding='latin1')

print("Filtrado completado. Se ha generado el archivo 'RESULTADO_FILTRADO.csv'.")