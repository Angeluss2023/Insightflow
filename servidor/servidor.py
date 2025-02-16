from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import csv
import subprocess
import torch
from werkzeug.utils import secure_filename
from flask import send_from_directory

from subprocess import Popen
from general import (
    leer_csv_y_unir,
    crear_carpeta_dataset_final,
    generar_nube_de_palabras,
    aplicar_modelo_pkl,
    aplicar_modelo_transformers,
    generar_grafico_pastel_modelo,
    generar_grafico_pastel_transformers
)

app = Flask(__name__)
CORS(app)

# Carpetas base para cada plataforma
BASE_FOLDERS = {
    "youtube": "./DatasetsYT",
    "tiktok": "./DatasetsTikTok",
    "web": "./DatasetsWeb"
}

# Archivos esperados para cada plataforma
EXPECTED_FILES = {
    "tiktok": [
        "comentarios_originales.csv",
        "comentarios_predictions.csv",
        "comentarios_preprocesados.csv",
        "comentarios_transformers.csv",
        "pie_chart_modelo.png",
        "pie_chart_transformers.png",
        "wordcloud.png"
    ],
    "youtube": [
        "comentarios_originales.csv",
        "comentarios_predictions.csv",
        "comentarios_preprocesados.csv",
        "comentarios_transformers.csv",
        "pie_chart_modelo.png",
        "pie_chart_transformers.png",
        "wordcloud.png"
    ],
    "web": [
        "comentarios_originales.csv",
        "comentarios_predictions.csv",
        "comentarios_preprocesados.csv",
        "comentarios_transformers.csv",
        "pie_chart_modelo.png",
        "pie_chart_transformers.png",
        "wordcloud.png"
    ]
}





# Extensiones permitidas para subir archivos
ALLOWED_EXTENSIONS = {'csv'}
# Extensiones permitidas para subir archivos
ALLOWED_EXTENSIONS = {'csv'}

# Variables de estado
data_extracted = {"tiktok": False, "youtube": False, "web": False}

# Crear carpetas base si no existen
for folder in BASE_FOLDERS.values():
    if not os.path.exists(folder):
        os.makedirs(folder)


# 🔹 Verificar formato del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 🔹 Obtener el dataset más reciente de una plataforma
def get_latest_dataset(platform):
    """
    Devuelve la ruta al dataset más reciente para la plataforma dada.
    """
    base_folder = BASE_FOLDERS.get(platform)
    if not base_folder:
        print(f"Base folder no configurada para {platform}")
        return None

    datasets = [os.path.join(base_folder, d) for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
    datasets.sort(key=os.path.getmtime, reverse=True)  # Ordenar por fecha de modificación

    if datasets:
        print(f"Datasets disponibles para {platform}: {datasets}")
        return datasets[0]
    else:
        print(f"No se encontraron datasets en {base_folder} para {platform}")
        return None


# 🔹 Enviar imágenes generadas (gráficos)
@app.route('/obtener_imagen/<platform>/<tipo_grafico>', methods=['GET'])
def obtener_imagen(platform, tipo_grafico):
    if platform not in BASE_FOLDERS and platform != "general":
        return jsonify({"error": f"Plataforma {platform} no válida."}), 400

    base_folder = BASE_FOLDERS.get(platform, "./DatasetsGeneral")
    if not os.path.exists(base_folder):
        return jsonify({"error": f"No se encontró una carpeta para {platform}."}), 404

    filename = f"{tipo_grafico}.png"
    latest_dataset = get_latest_dataset(platform) if platform != "general" else base_folder
    image_path = os.path.join(latest_dataset, filename)

    if not os.path.exists(image_path):
        return jsonify({"error": f"No se encontró el archivo {filename} para {platform}."}), 404

    return send_from_directory(latest_dataset, filename)




# 🔹 Obtener datos de una plataforma
@app.route('/obtener_datos/<platform>', methods=['GET'])
def obtener_datos(platform):
    """
    Verifica la existencia de los 4 archivos CSV y las 3 imágenes para YouTube, TikTok o Web, y devuelve los datos en formato JSON.
    """
    if platform not in BASE_FOLDERS:
        print(f"Plataforma no válida: {platform}")
        return jsonify({"error": f"Plataforma {platform} no válida."}), 400

    latest_dataset = get_latest_dataset(platform)
    print(f"Última carpeta para {platform}: {latest_dataset}")

    if not latest_dataset:
        print(f"No se encontraron datasets para la plataforma {platform}.")
        return jsonify({"error": f"No se encontraron datasets para {platform}."}), 404

    # Listas de archivos esperados
    expected_csv_files = [
        "comentarios_originales.csv",
        "comentarios_predictions.csv",
        "comentarios_preprocesados.csv",
        "comentarios_transformers.csv"
    ]
    expected_images = [
        "pie_chart_modelo.png",
        "pie_chart_transformers.png",
        "wordcloud.png"
    ]

    # Validar existencia de archivos
    missing_files = validate_files(latest_dataset, expected_csv_files + expected_images)

    if missing_files:
        print(f"Faltan archivos en el dataset {latest_dataset}: {missing_files}")
        return jsonify({
            "error": "Faltan archivos en el dataset.",
            "missing_files": missing_files,
            "dataset": latest_dataset
        }), 404

    # Leer el archivo principal de datos
    csv_path = os.path.join(latest_dataset, "comentarios_preprocesados.csv")
    if not os.path.exists(csv_path):
        print(f"El archivo principal no existe: {csv_path}")
        return jsonify({"error": f"El archivo {csv_path} no existe."}), 404

    try:
        data = []
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            columnas = reader.fieldnames
            columna_comentarios = next((col for col in ["Comentario", "comment"] if col in columnas), None)
            for row in reader:
                row["source"] = platform  # Agregar la fuente del comentario
                row["comment"] = row[columna_comentarios]  # Normalizar como "comment"
                data.append(row)

        print(f"Datos cargados exitosamente para {platform}: {len(data)} registros")
        return jsonify({
            "data": data[:20],  # Limitar a los primeros 15 registros
            "files": {
                "csv_files": [os.path.join(latest_dataset, file) for file in expected_csv_files],
                "images": [f"http://127.0.0.1:5000/{os.path.join(latest_dataset, image).replace('\\', '/')}" for image in expected_images]

            }
        }), 200

    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return jsonify({"error": f"Error al leer el archivo CSV: {e}"}), 500


def validate_files(dataset_path, expected_files):
    missing_files = []
    for file_name in expected_files:
        file_path = os.path.join(dataset_path, file_name)
        if not os.path.exists(file_path):
            print(f"Archivo faltante: {file_name}")
            missing_files.append(file_name)
    return missing_files



@app.route('/DatasetsYT/<dataset>/<filename>')
def serve_yt_file(dataset, filename):
    folder_path = os.path.join("DatasetsYT", dataset)
    print(f"Buscando archivo en: {os.path.join(folder_path, filename)}")
    if os.path.exists(os.path.join(folder_path, filename)):
        return send_from_directory(folder_path, filename)
    else:
        return jsonify({"error": "Archivo no encontrado"}), 404

@app.route('/DatasetsTikTok/<dataset>/<filename>')
def serve_tiktok_file(dataset, filename):
    folder_path = os.path.join("DatasetsTikTok", dataset)
    if os.path.exists(os.path.join(folder_path, filename)):
        return send_from_directory(folder_path, filename)
    else:
        return jsonify({"error": "Archivo no encontrado"}), 404


@app.route('/DatasetsWeb/<dataset>/<filename>')
def serve_web_file(dataset, filename):
    folder_path = os.path.join("DatasetsWeb", dataset)
    if os.path.exists(os.path.join(folder_path, filename)):
        return send_from_directory(folder_path, filename)
    else:
        return jsonify({"error": "Archivo no encontrado"}), 404


@app.route('/DATASETFINAL/<dataset>/<filename>', methods=['GET'])
def serve_dataset_file(dataset, filename):
    folder_path = os.path.join("DATASETFINAL", dataset)
    file_path = os.path.join(folder_path, filename)
    print(f"Buscando archivo en: {file_path}")  # Log para verificar la ruta
    if os.path.exists(file_path):
        return send_from_directory(folder_path, filename)
    else:
        return jsonify({"error": "Archivo no encontrado"}), 404


# 🔹 Obtener datos combinados de YouTube, TikTok y Web
@app.route('/procesar_datos_generales', methods=['GET'])
def procesar_datos_generales():
    try:
        # Directorios principales
        directorios = ['DatasetsTiktok', 'DatasetsWeb', 'DatasetsYT']
        
        # Leer y unir los CSV
        df_final = leer_csv_y_unir(directorios)
        
        # Validar si existe la columna 'comment' y filtrar valores no nulos
        if 'comment' in df_final.columns:
            df_final = df_final[df_final['comment'].notna()]  # Eliminar filas con NaN en 'comment'
        
        # Crear la carpeta DATASETFINAL y una nueva subcarpeta DatasetX
        base_path = 'DATASETFINAL'
        nueva_carpeta = crear_carpeta_dataset_final(base_path)
        
        # Guardar el archivo combinado
        ruta_archivo_final = os.path.join(nueva_carpeta, 'comentarios_unidos.csv')
        df_final.to_csv(ruta_archivo_final, index=False)
        
        # Generar nube de palabras
        if 'comment' in df_final.columns:
            comentarios = df_final['comment'].astype(str).tolist()
            generar_nube_de_palabras(comentarios, nueva_carpeta)
        
        # Aplicar modelos PKL y Transformers
        modelo_path = "modelo_sentimientos.pkl"
        vectorizer_path = "tfidf_vectorizer.pkl"
        aplicar_modelo_pkl(df_final, modelo_path, vectorizer_path, nueva_carpeta)
        aplicar_modelo_transformers(df_final, nueva_carpeta)
        
        # Generar gráficos de pastel
        generar_grafico_pastel_modelo(nueva_carpeta)
        generar_grafico_pastel_transformers(nueva_carpeta)
        
        # Obtener rutas de las imágenes generadas
        expected_images = [
            'nube_de_palabras.png',
            'grafico_pastel_modelo.png',
            'grafico_pastel_transformers.png'
        ]
        images = [
            os.path.join(nueva_carpeta, img).replace("\\", "/") for img in expected_images if os.path.exists(os.path.join(nueva_carpeta, img))
        ]
        
        # Preparar la respuesta
        response = {
            "data": df_final.fillna("").to_dict(orient='records'),  # Asegurar que no haya NaN
            "files": {
                "images": images
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar los datos generales: {str(e)}"}), 500


# 🔹 Recibir archivos y guardarlos en su carpeta correspondiente
@app.route('/recibir_archivos/<platform>', methods=['POST'])
def recibir_archivos(platform):
    """
    Guarda archivos en la carpeta correcta según la plataforma (YouTube, TikTok, Web).
    """
    if platform not in BASE_FOLDERS:
        return jsonify({"error": f"Plataforma {platform} no válida."}), 400

    latest_dataset = get_latest_dataset(platform)
    if not latest_dataset:
        return jsonify({"error": f"No se encontró un dataset reciente para {platform}."}), 404

    try:
        files_to_save = {
            "csv": f"{platform}_comments_preprocessed.csv",
            "wordcloud": "wordcloud.png",
            "pie_chart_modelo": "pie_chart_modelo.png",
            "pie_chart_transformers": "pie_chart_transformers.png"
        }

        saved_paths = {}

        for file_key, filename in files_to_save.items():
            if file_key in request.files:
                file = request.files[file_key]
                if file.filename == '':
                    return jsonify({"error": f"El archivo {file_key} no tiene un nombre válido."}), 400
                file_path = os.path.join(latest_dataset, filename)
                file.save(file_path)
                saved_paths[file_key] = file_path

        return jsonify({
            "mensaje": "Archivos recibidos y guardados con éxito",
            "archivos": saved_paths
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar los archivos: {e}"}), 500


# 🔹 Servir archivos estáticos
@app.route('/datasets/<platform>/<dataset>/<filename>', methods=['GET'])
def serve_file(platform, dataset, filename):
    """
    Sirve archivos desde las carpetas específicas para cada plataforma.
    """
    # Validar la plataforma
    if platform not in BASE_FOLDERS:
        return jsonify({"error": f"Plataforma {platform} no válida."}), 400

    # Construir la ruta completa al archivo
    folder_path = os.path.join(BASE_FOLDERS[platform], dataset)
    file_path = os.path.join(folder_path, filename)

    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        return jsonify({"error": f"El archivo {filename} no se encontró en {platform}/{dataset}."}), 404

    # Servir el archivo
    return send_from_directory(folder_path, filename)


@app.route('/realizar_busqueda', methods=['POST'])
def realizar_busqueda():
    try:
        data = request.get_json()
        search_term = data.get('search_term')

        if not search_term:
            return jsonify({"error": "El término de búsqueda es obligatorio."}), 400

        # Ejecutar los scripts con el término de búsqueda
        scripts = [
            ("tiktok.py", search_term),
            ("youtube.py", search_term),
            ("web.py", search_term)
        ]

        for script, term in scripts:
            Popen(["python", script, term])

        return jsonify({"mensaje": "Búsqueda iniciada con éxito."}), 200

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500
    
# 🔹 Ejecutar extracción de datos
@app.route('/ejecutar_extraccion', methods=['POST'])
def ejecutar_extraccion():
    """
    Ejecuta los scripts en paralelo para extraer datos y verifica la generación de archivos.
    """
    try:
        scripts_info = [
            {"script": "tiktok.py", "platform": "tiktok"},
            {"script": "youtube.py", "platform": "youtube"},
            {"script": "breadsoupautomatico.py", "platform": "web"}
        ]

        # Ejecutar scripts en paralelo
        processes = []
        for script in scripts_info:
            process = subprocess.Popen(
                ["python", script["script"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            processes.append((process, script["platform"]))

        # Esperar a que todos los procesos terminen
        for process, platform in processes:
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                print(f"❌ Error al ejecutar {platform}: {stderr}")
                return jsonify({"error": f"Error en {platform}: {stderr}"}), 500

        print("[INFO] Extracción completada. Verificando archivos generados...")

        # Verificar archivos generados
        problemas_datasets = {}
        for platform in ["tiktok", "youtube", "web"]:
            latest_dataset = get_latest_dataset(platform)
            if not latest_dataset:
                problemas_datasets[platform] = "No se encontró ningún dataset."
                continue

            missing_files = []
            for file_name in EXPECTED_FILES[platform]:
                file_path = os.path.join(latest_dataset, file_name)
                if not os.path.exists(file_path):
                    missing_files.append(file_name)

            if missing_files:
                problemas_datasets[platform] = f"Faltan archivos: {missing_files}"

        if problemas_datasets:
            print(f"[ERROR] Problemas con los datasets: {problemas_datasets}")
            return jsonify({
                "error": "Problemas con los datasets.",
                "details": problemas_datasets
            }), 500

        # Si todo está bien
        return jsonify({"mensaje": "Extracción completada correctamente"}), 200

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return jsonify({"error": f"Error inesperado: {e}"}), 500


# 🔹 Inicio del servidor
if __name__ == "__main__":
    app.run(debug=True)
