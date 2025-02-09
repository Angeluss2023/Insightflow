import os
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# NUEVAS IMPORTACIONES PARA LOS MODELOS
from joblib import load  # Para cargar el modelo PKL y el vectorizador
from transformers import pipeline  # Para el modelo Transformers

def encontrar_ultima_carpeta(directorio):
    # Listar todas las carpetas en el directorio
    carpetas = [carpeta for carpeta in os.listdir(directorio) if os.path.isdir(os.path.join(directorio, carpeta))]
    
    # Filtrar solo carpetas que sigan el formato DatasetX
    carpetas = [carpeta for carpeta in carpetas if carpeta.startswith('Dataset') and carpeta[7:].isdigit()]
    
    # Ordenar las carpetas numéricamente
    carpetas.sort(key=lambda x: int(x.replace('Dataset', '')))
    
    # Devolver la última carpeta
    if carpetas:
        return os.path.join(directorio, carpetas[-1])
    else:
        raise FileNotFoundError(f"No se encontraron carpetas válidas en {directorio}")

def leer_csv_y_unir(directorios):
    dataframes = []
    
    for directorio in directorios:
        try:
            # Encontrar la última carpeta
            ultima_carpeta = encontrar_ultima_carpeta(directorio)
            
            # Construir la ruta al archivo CSV
            ruta_csv = os.path.join(ultima_carpeta, 'comentarios_preprocesados.csv')
            
            # Leer el CSV y agregarlo a la lista de DataFrames
            if os.path.exists(ruta_csv):
                df = pd.read_csv(ruta_csv)
                dataframes.append(df)
            else:
                print(f"El archivo {ruta_csv} no existe.")
        except FileNotFoundError as e:
            print(e)
    
    # Unir todos los DataFrames en uno solo
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        return pd.DataFrame()

def crear_carpeta_dataset_final(base_path):
    # Si no existe la carpeta base, la creamos
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    # Listar todas las carpetas dentro de la carpeta base
    carpetas = [carpeta for carpeta in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, carpeta))]
    
    # Filtrar solo carpetas que sigan el formato DatasetX
    carpetas = [carpeta for carpeta in carpetas if carpeta.startswith('Dataset') and carpeta[7:].isdigit()]
    
    # Encontrar el número más alto de las carpetas DatasetX
    if carpetas:
        carpetas.sort(key=lambda x: int(x.replace('Dataset', '')))
        ultimo_numero = int(carpetas[-1].replace('Dataset', ''))
        nuevo_numero = ultimo_numero + 1
    else:
        nuevo_numero = 1
    
    # Crear la nueva carpeta DatasetX
    nueva_carpeta = os.path.join(base_path, f'Dataset{nuevo_numero}')
    os.makedirs(nueva_carpeta)
    
    return nueva_carpeta

def generar_nube_de_palabras(comentarios, ruta_carpeta):
    """
    Genera una nube de palabras a partir de los comentarios del dataset unido,
    usando solo las palabras relevantes (máximo 10) relacionadas con la aceptación de la IA.
    """
    # Definir el conjunto de 10 palabras relevantes (ajusta según tus necesidades)
    relevant_words = {"bueno", "malo", "futuro", "ético", "ia", "innovación", "aceptación", "eficacia", "confiable", "riesgo", "rápido", "genial", "horrible"}
    
    # Extraer y filtrar palabras relevantes de cada comentario
    palabras_filtradas = []
    for comentario in comentarios:
        # Convertir el comentario a minúsculas y separar en palabras
        for palabra in comentario.lower().split():
            if palabra in relevant_words:
                palabras_filtradas.append(palabra)
    
    # Contar la frecuencia de las palabras relevantes
    frecuencias = Counter(palabras_filtradas)
    
    # Seleccionar solo las 10 palabras más comunes (si hay menos, se usarán todas)
    comunes = dict(frecuencias.most_common(10))
    
    if not comunes:
        print("No se encontraron palabras relevantes para la nube de palabras.")
        return
    
    # Generar la nube de palabras a partir de las frecuencias
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(comunes)
    
    # Guardar la imagen de la nube de palabras
    ruta_imagen = os.path.join(ruta_carpeta, 'nube_de_palabras.png')
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(ruta_imagen)
    plt.close()
    print(f"🌥 Nube de palabras guardada en: {ruta_imagen}")

def generar_grafico_pastel(comentarios, ruta_carpeta):
    """
    (Esta función original se conserva para otros fines, pero no se usará en este caso.)
    """
    # Convertir cada comentario a cadena, unir y separar en palabras
    palabras = ' '.join(map(str, comentarios)).split()
    frecuencias = Counter(palabras)
    
    # Obtener las 10 palabras más comunes
    palabras_comunes = frecuencias.most_common(10)
    if palabras_comunes:
        palabras, frec = zip(*palabras_comunes)
    else:
        palabras, frec = [], []
    
    # Crear el gráfico de pastel
    plt.figure(figsize=(8, 8))
    plt.pie(frec, labels=palabras, autopct='%1.1f%%', startangle=140)
    plt.title('Top 10 palabras más comunes')
    
    # Guardar el gráfico de pastel como imagen
    ruta_imagen = os.path.join(ruta_carpeta, 'grafico_pastel.png')
    plt.savefig(ruta_imagen)
    plt.close()
    print(f"🥧 Gráfico de pastel guardado en: {ruta_imagen}")

# =================== NUEVAS FUNCIONES DE MODELO ========================

def aplicar_modelo_pkl(df, model_path, vectorizer_path, output_path):
    """
    Carga el modelo PKL y el vectorizador, aplica la predicción sobre la columna 'comment'
    del DataFrame y guarda un CSV con las predicciones.
    """
    try:
        modelo = load(model_path)
        vectorizador = load(vectorizer_path)
    except Exception as e:
        print(f"Error al cargar el modelo o vectorizador: {e}")
        return

    # Verificar que la columna 'comment' exista y convertirla a string
    if 'comment' not in df.columns:
        print("La columna 'comment' no se encuentra en el DataFrame.")
        return

    comentarios = df['comment'].astype(str).tolist()
    try:
        comentarios_tfidf = vectorizador.transform(comentarios)
        predicciones = modelo.predict(comentarios_tfidf)
    except Exception as e:
        print(f"Error al aplicar el modelo: {e}")
        return

    # Crear un DataFrame con los comentarios y sus predicciones
    df_predicciones = pd.DataFrame({
        'comment': comentarios,
        'prediccion_modelo': predicciones
    })

    # Guardar el DataFrame a CSV
    ruta_csv = os.path.join(output_path, 'prediccion_modelo.csv')
    df_predicciones.to_csv(ruta_csv, index=False)
    print(f"✅ CSV con predicciones del modelo PKL guardado en: {ruta_csv}")

from transformers import pipeline
import torch

def aplicar_modelo_transformers(df, output_path):
    """
    Utiliza el modelo Transformers para analizar el sentimiento de los comentarios y guarda
    un CSV con las predicciones.
    """
    # Verificar que la columna 'comment' exista y convertirla a string
    if 'comment' not in df.columns:
        print("La columna 'comment' no se encuentra en el DataFrame.")
        return

    # Configurar dispositivo para GPU o CPU
    device = 0 if torch.cuda.is_available() else -1
    print(f"Usando {'GPU' if device == 0 else 'CPU'} para Transformers.")

    # Cargar el modelo Transformers con el dispositivo adecuado
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model="nlptown/bert-base-multilingual-uncased-sentiment", 
        device=device
    )

    comentarios = df['comment'].astype(str).tolist()
    predicciones_transformers = []
    
    # Procesar cada comentario (se truncan a 512 caracteres si es necesario)
    for comentario in comentarios:
        try:
            resultado = sentiment_pipeline(comentario[:512])[0]
            predicciones_transformers.append(resultado['label'])
        except Exception as e:
            print(f"Error al procesar el comentario: {e}")
            predicciones_transformers.append("NEUTRAL")

    # Crear un DataFrame con las predicciones de Transformers
    df_transformers = pd.DataFrame({
        'comment': comentarios,
        'prediccion_transformers': predicciones_transformers
    })

    # Guardar el DataFrame a CSV
    ruta_csv = os.path.join(output_path, 'prediccion_transformers.csv')
    df_transformers.to_csv(ruta_csv, index=False)
    print(f"✅ CSV con predicciones de Transformers guardado en: {ruta_csv}")


# =================== NUEVAS FUNCIONES DE GRÁFICOS PASTEL ========================

def generar_grafico_pastel_modelo(output_path):
    """
    Carga 'prediccion_modelo.csv' y genera un gráfico de pastel basado en la cantidad
    de comentarios positivos y negativos. Se asume que 1 es positivo y 0 es negativo.
    """
    ruta_csv = os.path.join(output_path, 'prediccion_modelo.csv')
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        print(f"Error al leer {ruta_csv}: {e}")
        return

    # Contar positivos y negativos (se asume: 1 = positivo, 0 = negativo)
    positivos = (df['prediccion_modelo'] == 1).sum()
    negativos = (df['prediccion_modelo'] == 0).sum()

    etiquetas = ['Positivos', 'Negativos']
    cantidades = [positivos, negativos]

    plt.figure(figsize=(8, 8))
    plt.pie(cantidades, labels=etiquetas, autopct='%1.1f%%', startangle=140, colors=['#99ff99','#ff9999'])
    plt.title('Distribución de Sentimientos (Modelo PKL)')
    ruta_imagen = os.path.join(output_path, 'grafico_pastel_modelo.png')
    plt.savefig(ruta_imagen)
    plt.close()
    print(f"🥧 Gráfico de pastel del modelo PKL guardado en: {ruta_imagen}")

def generar_grafico_pastel_transformers(output_path):
    """
    Carga 'prediccion_transformers.csv' y genera un gráfico de pastel basado en la cantidad
    de comentarios para cada etiqueta: Muy Negativo, Negativo, Neutral, Positivo y Muy Positivo.
    """
    ruta_csv = os.path.join(output_path, 'prediccion_transformers.csv')
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        print(f"Error al leer {ruta_csv}: {e}")
        return

    # Mapeo de etiquetas de stars a categorías deseadas
    mapeo = {
        "1 star": "Muy Negativo",
        "2 stars": "Negativo",
        "3 stars": "Neutral",
        "4 stars": "Positivo",
        "5 stars": "Muy Positivo"
    }
    
    # Convertir cada etiqueta usando el mapeo; si no se encuentra, se asigna "Neutral"
    etiquetas_mapeadas = df['prediccion_transformers'].apply(lambda x: mapeo.get(x, "Neutral"))
    
    # Contar las ocurrencias de cada categoría
    conteos = etiquetas_mapeadas.value_counts()
    
    # Ordenar en el orden deseado (si existen todas las categorías)
    orden = ["Muy Negativo", "Negativo", "Neutral", "Positivo", "Muy Positivo"]
    cantidades = [conteos.get(clave, 0) for clave in orden]
    
    plt.figure(figsize=(8, 8))
    plt.pie(cantidades, labels=orden, autopct='%1.1f%%', startangle=140, colors=['#ff6666','#ffcc66','#cccccc','#99ff99','#66b3ff'])
    plt.title('Distribución de Sentimientos (Transformers)')
    ruta_imagen = os.path.join(output_path, 'grafico_pastel_transformers.png')
    plt.savefig(ruta_imagen)
    plt.close()
    print(f"🥧 Gráfico de pastel de Transformers guardado en: {ruta_imagen}")

# =================== FIN NUEVAS FUNCIONES ========================

def main():
    # Definir los directorios principales
    directorios = [
        'DatasetsTiktok',
        'DatasetsWebs',
        'DatasetsYT',
    ]
    
    # Leer y unir los CSV
    df_final = leer_csv_y_unir(directorios)
    
    # Crear la carpeta DATASETFINAL y una nueva subcarpeta DatasetX
    base_path = 'DATASETFINAL'
    nueva_carpeta = crear_carpeta_dataset_final(base_path)
    
    # Guardar el archivo comentarios_unidos.csv en la nueva carpeta
    ruta_archivo_final = os.path.join(nueva_carpeta, 'comentarios_unidos.csv')
    df_final.to_csv(ruta_archivo_final, index=False)
    print(f"📄 Archivo CSV guardado en: {ruta_archivo_final}")
    
    # Generar nube de palabras a partir de todos los comentarios del dataset unido
    if 'comment' in df_final.columns:
        comentarios = df_final['comment'].astype(str).tolist()
        generar_nube_de_palabras(comentarios, nueva_carpeta)
    else:
        print("La columna 'comment' no existe en el DataFrame final, no se generará la nube de palabras.")
    
    # =============================================================
    # Aplicar el modelo PKL con vectorizador para predecir la emoción
    # =============================================================
    modelo_path = "modelo_sentimientos.pkl"
    vectorizer_path = "tfidf_vectorizer.pkl"
    aplicar_modelo_pkl(df_final, modelo_path, vectorizer_path, nueva_carpeta)
    
    # =============================================================
    # Aplicar el modelo Transformers para predecir la emoción
    # =============================================================
    aplicar_modelo_transformers(df_final, nueva_carpeta)
    
    # =============================================================
    # Generar gráficos de pastel con la distribución de sentimientos
    # =============================================================
    generar_grafico_pastel_modelo(nueva_carpeta)
    generar_grafico_pastel_transformers(nueva_carpeta)

if __name__ == "__main__":
    main()