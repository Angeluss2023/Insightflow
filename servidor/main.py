import subprocess
import os
import requests
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = {
    "tiktok": "./DatasetsTikTok",
    "youtube": "./DatasetsYT",
    "web": "./DatasetsWeb"
}

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

# Crear una barrera para sincronizar los hilos (una por cada script que ejecutamos)

def ejecutar_script(script_name, platform):
    """Ejecuta un script en un subproceso y verifica la creación de archivos."""
    try:
        print(f"🔄 Ejecutando {script_name} para {platform}...")

        proceso = subprocess.Popen(
            ["python", script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        try:
            stdout, stderr = proceso.communicate(timeout=300)  # Tiempo máximo de espera
        except subprocess.TimeoutExpired:
            proceso.kill()
            print(f"⏳ El script {script_name} excedió el tiempo límite y fue terminado.")
            return False

        if proceso.returncode != 0:
            print(f"❌ Error en {script_name}: {stderr.strip()}")
            return False

        print(f"✅ {script_name} ejecutado correctamente.")

        # Validar archivos generados
        latest_dataset = os.path.join(
            BASE_DIR[platform],
            max(os.listdir(BASE_DIR[platform]), key=lambda x: int(x.replace("Dataset", "")))
        )
        missing_files = [
            file_name for file_name in EXPECTED_FILES[platform]
            if not os.path.exists(os.path.join(latest_dataset, file_name))
        ]

        if missing_files:
            print(f"⚠️ Faltan archivos en {platform}: {missing_files}")
            return False

        print(f"✅ Todos los archivos necesarios están presentes para {platform}.")
        return True

    except Exception as e:
        print(f"⚠️ Error al ejecutar {script_name}: {e}")
        return False

