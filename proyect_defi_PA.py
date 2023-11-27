import streamlit as st
import pandas as pd
import numpy as np

# Diccionario con la información de los archivos
archivos_excel = {
    "Encuesta 1": {"file": "archivo_500_LIMA.xlsx", "count_column": 'P506', "df_column_name": 'EN LOS ÚLTIMOS 12 MESES, ¿CON QUÉ FRECUENCIA LEYÓ O LE LEYERON LIBROS IMPRESOS O DIGITALES'},
    "Encuesta 2": {"file": "archivo_300_400_LIMA.xlsx", "count_column": 'P307_1', "df_column_name": '¿SABE LEER Y ESCRIBIR EN CASTELLANO?'},
    "Encuesta 3": {"file": "archivo_500_LIMA.xlsx", "count_column": 'P501_4_1', "df_column_name": 'En el mes pasado,¿Conto un relato, cuento, historia, declamo, recito?'},
    "Encuesta 4": {"file": "archivo_300_400_LIMA.xlsx", "count_column": 'P403', "df_column_name": '¿Con qué frecuencia usted ha leído libros, periódicos, revistas u otros contenidos impresos y/o digitales?'},
    "Encuesta 5": {"file": "archivo_600_LIMA.xlsx", "count_column": 'P601', "df_column_name": '¿CUÁNTOS LIBROS IMPRESOS TIENE EL HOGAR?'}
}

nuevos_valores = {
    "Encuesta 1": {
        1: 'Diariamente',
        2: 'Varias veces a la semana',
        3: 'Una vez a la semana',
        4: 'Varias veces al mes',
        5: 'Una vez al mes',
        6: 'Una vez cada tres meses',
        7: 'Por lo menos una vez al año',
        8: 'NO LEYÓ / NO LE LEYERON',
        9: 'NO SABE/NO RESPONDE'
    },
    "Encuesta 4": {
        1: 'Diariamente',
        2: 'Varias veces a la semana',
        3: 'Una vez a la semana',
        4: 'Una vez al mes',
        5: 'Una vez cada tres meses',
        6: 'Por lo menos una vez al año'
    },
    "Encuesta 2": {
        1: 'Si',
        2: 'No'
    },
    "Encuesta 3": {
        1: 'Si',
        2: 'No',
        3: 'No sabe'
    }
}

st.title('Encuesta Nacional de Lectura')

# Crear un cuadro combinado para seleccionar el archivo de Excel
encuesta_seleccionada = st.selectbox("Selecciona una encuesta a continuación", list(archivos_excel.keys()))

# Obtener la información del archivo seleccionado
archivo_seleccionado = archivos_excel[encuesta_seleccionada]["file"]
columna_conteo = archivos_excel[encuesta_seleccionada]["count_column"]
nombre_columna = archivos_excel[encuesta_seleccionada]["df_column_name"]

# Leer solo la columna necesaria del archivo de Excel seleccionado
df = pd.read_excel(archivo_seleccionado, usecols=[columna_conteo, 'NOMBREDI'])

# Leer el archivo de Excel con las coordenadas de los distritos
df_coordenadas = pd.read_excel("localizador_actualizado.xlsx", usecols=['NOMBDIST', 'Geo_Point'], index_col='NOMBDIST')

# Dividir la columna 'Geo_Point' en dos columnas 'Latitud' y 'Longitud'
df_coordenadas[['lat', 'lon']] = df_coordenadas['Geo_Point'].str.split(',', expand=True)

# Crear un diccionario con las coordenadas de los distritos
coordenadas_distritos = df_coordenadas[['lat', 'lon']].T.to_dict('list')

# Agregar las coordenadas de latitud y longitud a tu DataFrame
df['lat'] = df['NOMBREDI'].map(lambda x: float(coordenadas_distritos[x][0]) if x in coordenadas_distritos else None)
df['lon'] = df['NOMBREDI'].map(lambda x: float(coordenadas_distritos[x][1]) if x in coordenadas_distritos else None)


# Contar la frecuencia de los valores en la columna especificada
conteo = df[columna_conteo].value_counts(dropna=False)

if encuesta_seleccionada in nuevos_valores:
    conteo.index = conteo.index.to_series().replace(nuevos_valores[encuesta_seleccionada])

# Crear un nuevo DataFrame con los resultados
df_conteo = pd.DataFrame({
    nombre_columna: conteo.index,
    'cantidad total': conteo.values
})

if encuesta_seleccionada == "Encuesta 5":
    df_conteo[nombre_columna] = df_conteo[nombre_columna].apply(lambda x: f"{x} libro" if x == 1 else f"{x} libros")

# Mostrar el DataFrame en Streamlit
st.dataframe(df_conteo)

# Mostrar un gráfico de barras en Streamlit
st.bar_chart(df_conteo.set_index(nombre_columna))

distrito_seleccionado = st.selectbox("Selecciona un distrito", df['NOMBREDI'].unique())

# Filtrar el DataFrame con los datos del distrito seleccionado
df_distrito = df[df['NOMBREDI'] == distrito_seleccionado]


# Contar la frecuencia de los valores en la columna especificada para el distrito seleccionado
conteo_distrito = df_distrito[columna_conteo].value_counts(dropna=False)

if encuesta_seleccionada in nuevos_valores:
    conteo_distrito.index = conteo_distrito.index.to_series().replace(nuevos_valores[encuesta_seleccionada])

# Crear un nuevo DataFrame con los resultados para el distrito seleccionado
df_conteo_distrito = pd.DataFrame({
    nombre_columna: conteo_distrito.index,
    'cantidad total': conteo_distrito.values
})

if encuesta_seleccionada == "Encuesta 5":
    df_conteo_distrito[nombre_columna] = df_conteo_distrito[nombre_columna].apply(lambda x: f"{x} libro" if x == 1 else f"{x} libros")

# Mostrar el DataFrame de la encuesta del distrito seleccionado en Streamlit
st.dataframe(df_conteo_distrito)

# Crear un mapa interactivo con las coordenadas del distrito seleccionado
st.map(df_distrito)
